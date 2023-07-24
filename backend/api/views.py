from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.pagination import LimitPagination
from api.serializers import (CreateRecipeSerializer, FollowSerializer,
                             IngredientSerializer, ShortRecipeSerializer,
                             ShowRecipeSerializer, TagSerializer)
from api.filters import IngredientFilter, RecipeFilter
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow
from api.permissions import AdminOrReadOnly

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPagination

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        '''Подписки.'''
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        '''Подписка / Отписка.'''
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'Ошибка': 'На себя нельзя подписаться / отписаться'},
                status=status.HTTP_400_BAD_REQUEST)
        follow = user.follower.filter(author=author)
        if request.method == 'POST':
            if follow.exists():
                return Response(
                    'Вы уже подписаны', status=status.HTTP_400_BAD_REQUEST
                )
            queryset = Follow.objects.create(author=author, user=user)
            serializer = FollowSerializer(
                queryset, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not follow.exists():
            return Response(
                {'Ошибка': 'Нельзя отписаться повторно'},
                status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def add_to(self, model, user, pk):
        '''Добавление рецепта в избранное / корзину.'''
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'Ошибка': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        '''Удаление рецепта из избранного / корзины.'''
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'Ошибка': 'Рецепт уже удален'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True,
            url_path='favorite', url_name='favorite',
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        '''Избранное.'''
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        '''Корзина.'''
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    def create_shopping_cart(self, ingredients, user):
        '''Формирование корзины для скачивания.'''
        shopping_list = ('Список покупок\n\n')
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        '''Скачивание корзины.'''
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.create_shopping_cart(ingredients, user)
