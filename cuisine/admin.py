from django.contrib import admin

from .models import Dish, Tag, Ingredient, IngredientPosition, Meal, MealPosition, MenuCategory


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'menu_type')


class TagInline(admin.TabularInline):
    model = Dish.tags.through
    extra = 1


class IngredientPositionInline(admin.TabularInline):
    model = IngredientPosition
    extra = 3


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    inlines = (TagInline, IngredientPositionInline)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


class MealPositionInline(admin.TabularInline):
    model = MealPosition
    extra = 1


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    inlines = (MealPositionInline,)
