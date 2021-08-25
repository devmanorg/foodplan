from django.contrib import admin

from .models import Dish, Tag, Ingridient, IngridientPosition, Meal, MealPosition


class TagInline(admin.TabularInline):
    model = Dish.tags.through
    extra = 1


class IngridientPostionInline(admin.TabularInline):
    model = IngridientPosition
    extra = 3


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    inlines = (TagInline, IngridientPostionInline)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ('name',)


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    pass


class MealPositionInline(admin.TabularInline):
    model = MealPosition
    extra = 1


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    inlines = (MealPositionInline,)
