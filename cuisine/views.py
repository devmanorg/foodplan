import datetime
import random

from django.shortcuts import render, get_object_or_404
from contextlib import suppress

from .models import Meal, Dish, MealPosition

from django.db import connection


def show_next_week_menu(request):
    user_id = 1  #TODO get customer
    weekdays = count_days(7)

    meals = (
        Meal.objects
        .filter(date__in=weekdays)
        .filter(customer=user_id)
        .prefetch_related('meal_positions')
    )

    meals_per_day = ((day, meals.filter(date=day)) for day in weekdays)

    serialized_meals = {}
    for day, daily_serving in meals_per_day:
        daily_dishes = {}
        with suppress(Meal.DoesNotExist):
            daily_dishes.setdefault('breakfast', daily_serving.get(meal_type='BREAKFAST'))
            daily_dishes.setdefault('lunch', daily_serving.get(meal_type='LUNCH'))
            daily_dishes.setdefault('dinner', daily_serving.get(meal_type='DINNER'))
        serialized_meals.setdefault(day, daily_dishes)

    return render(
        request, 'temp_week_menu.html',
        context={'meals': serialized_meals}
    )


def calculate_products(request):
    days_to_calculate = 1
    weekdays = count_days(days_to_calculate)

    ingredients = (
        Meal.objects
        .filter(date__in=weekdays)
        .values_list(
            'meal_positions__dish__positions__ingredient__name',
            'meal_positions__dish__positions__quantity',
        )
    )

    total_ingredients = {}
    for ingredient, quantity in ingredients:
        total_ingredients.setdefault(ingredient, 0)
        total_ingredients[ingredient] += quantity

    return render(
        request,
        'temp_calc.html',
        context={'ingredients': total_ingredients},
    )


def view_recipe(request, recipe_id):
    dish = get_object_or_404(Dish, pk=recipe_id)
    print(len(connection.queries))
    return render(request, 'temp_recipe.html', context={'recipe': dish})


def count_days(days_count):
    return [
        datetime.date.today() + datetime.timedelta(days=day)
        for day in range(1, days_count + 1)
    ]


def show_daily_menu(request):
    random_breakfast = random.choice(MealPosition.objects. \
                                     filter(meal__meal_type='BREAKFAST'))
    random_launch = random.choice(MealPosition.objects. \
                                  filter(meal__meal_type='LUNCH'))
    random_dinner = random.choice(MealPosition.objects. \
                                  filter(meal__meal_type='DINNER'))
    context = {'breakfast': random_breakfast,
               'launch': random_launch,
               'dinner': random_dinner
               }
    return render(request, 'daily_menu.html', context=context)
