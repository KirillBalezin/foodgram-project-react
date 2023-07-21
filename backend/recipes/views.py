from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from recipes.models import (
    Ingredient,
    IngredientAmount,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
)
from recipes.serializers import (
    IngredientSerializer,
    TagSerializer,
    ShowRecipeSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from recipes.filters import RecipeFilter, IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permissions = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST' or method == 'PATCH':
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteViewSet(APIView):
    permissions = (IsAuthenticatedOrReadOnly,)

    @action(methods=['POST'], detail=True,)
    def post(self, request, recipe_id):
        '''Добавление рецепта в избранное.'''
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            return Response(
                {'Ошибка': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=True,)
    def delete(self, request, recipe_id):
        '''Удаление рецепта из избранного.'''
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    @action(methods=['POST'], detail=True)
    def post(self, request, recipe_id):
        '''Добавление рецепта в корзину.'''
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        if ShoppingCart.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            return Response(
                {'Ошибка': 'Рецепт же есть в корзине'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(method=['DELETE'], detail=True)
    def delete(self, request, recipe_id):
        '''Удаление рецепта из корзины.'''
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    '''Cкачивание корзины.'''
    user = request.user
    shopping_cart = user.shopping_cart.all()
    buying_list = {}
    for record in shopping_cart:
        recipe = record.recipe
        ingredients = IngredientAmount.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount,
                }
            else:
                buying_list[name]['amount'] = (
                    buying_list[name]['amount'] + amount
                )
    wishlist = []
    for name, data in buying_list.items():
        wishlist.append(
            f"{name} - {data['amount']} {data['measurement_unit']}"
        )
    response = HttpResponse(wishlist, content_type='text/plain')
    return response
