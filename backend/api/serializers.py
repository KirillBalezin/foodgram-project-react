from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import ValidationError

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)

    def create(self, validated_data):
        '''Создание пользователя.'''
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        '''Статус подписки на автора.'''
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                author=obj.author, user=request.user).exists()
        )

    def get_recipes(self, obj):
        '''Получение списка рецептов автора.'''
        limit = self.context.get('request').GET.get('recipes_limit')
        recipe_obj = obj.author.recipes.all()
        if limit:
            recipe_obj = recipe_obj[:int(limit)]
        serializer = ShortRecipeSerializer(recipe_obj, many=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.favorite.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_cart.filter(recipe=obj).exists()
        )


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True, write_only=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',)

    @staticmethod
    def create_ingredient_amount(valid_ingredients, recipe):
        '''Добавление ингредиентов'''
        for ingredient in valid_ingredients:
            ingredient_model = ingredient['id']
            amount = ingredient['amount']
            IngredientAmount.objects.create(
                ingredient=ingredient_model, recipe=recipe, amount=amount
            )

    def validate_cooking_time(self, data):
        '''Валидация времени приготовления.'''
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Время не может быть менее минуты.')
        return data

    def validate_ingredients(self, data):
        '''Валидация ингредиентов.'''
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'Хотя бы один ингредиент должен быть указан.'
            )
        unique_ingredient = []
        for ingredient in ingredients:
            if ingredient['id'] in unique_ingredient:
                raise ValidationError('Нельзя дублировать ингредиенты.')
            unique_ingredient.append(ingredient['id'])
            if int(ingredient['amount']) < 1:
                raise ValidationError('Количество не может быть менее 1.')
        return data

    def validate_tags(self, data):
        '''Валидация тегов.'''
        tags = self.initial_data.get('tags', False)
        if not tags:
            raise ValidationError('Хотя бы один тэг должен быть указан.')
        unique_tags = []
        for tag in tags:
            if tag in unique_tags:
                raise ValidationError('Нельзя дублировать теги.')
            unique_tags.append(tag)
        return data

    def create(self, validated_data):
        '''Создание рецепта.'''
        valid_ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredient_amount(valid_ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        '''Обновление рецепта.'''
        tags_data = validated_data.pop('tags')
        valid_ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.create_ingredient_amount(valid_ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShowRecipeSerializer(instance, context=self.context).data
