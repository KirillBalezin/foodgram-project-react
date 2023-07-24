from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    '''Кастомная админка для модели Tag.'''
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    '''Кастомная админка для модели Ingredient.'''
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    '''Кастомная админка для модели Recipe.'''
    list_display = (
        'pk',
        'name',
        'author',
        'image',
        'count_added'
    )
    exclude = ('ingredients',)
    inlines = (IngredientAmountInline,)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'name', 'tags__name')
    empty_value_display = '-пусто-'

    def count_added(self, obj):
        return obj.favorite.count()


class FavoriteShoppingAdmin(admin.ModelAdmin):
    '''Кастомная админка для моделей Favorite и ShoppingCart.'''
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorite, FavoriteShoppingAdmin)
admin.site.register(ShoppingCart, FavoriteShoppingAdmin)
