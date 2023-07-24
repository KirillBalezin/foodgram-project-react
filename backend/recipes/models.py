from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_LENGTH_NAME = 256
MAX_LENGTH_SLUG = 50
MAX_LENGTH_COLOR = 7


class Tag(models.Model):
    '''Модель тега.'''

    COLOR_PALETTE = [
        ('#FFFFFF', 'white', ),
        ('#000000', 'black', ),
    ]

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название тега',
    )
    color = ColorField(
        samples=COLOR_PALETTE,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Slug тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель ингредиента.'''
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецепта.'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsInRecipe',
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagsInRecipe(models.Model):
    '''Связь рецепта и тэгов.'''
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег в рецепте',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Теги в рецепте"
        verbose_name_plural = verbose_name
        unique_together = ('tag', 'recipe')


class IngredientAmount(models.Model):
    '''Связь рецепта и ингредиентов.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = verbose_name
        unique_together = ('ingredient', 'recipe')


class Favorite(models.Model):
    '''Модель избранное.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        default_related_name = 'favorite'
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    '''Модель корзины.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        default_related_name = 'shopping_cart'
        unique_together = ('user', 'recipe')
