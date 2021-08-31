import logging
import math
import random
import datetime
from typing import List, Dict, Sequence

from django.contrib.auth.models import User

from cuisine.models import MealPosition, Dish, Meal


def regenerate_and_save_menu(user: User):
    meals = Meal.objects.filter(customer=user)
    all_dishes = Dish.objects.prefetch_related('tags')

    for meal_type in Meal.MEAL_TYPES:
        meal_type_dishes = all_dishes.filter(tags__name=meal_type[1]).all()
        meal_type_dishes = _get_random_dishes(meal_type_dishes, count=7)

        for i, date in enumerate(generate_dates_from_today(days_count=7)):
            if meals.filter(date=date, meal_type=meal_type[0]).exists():
                continue

            meal = Meal.objects.create(meal_type=meal_type[0], date=date, customer=user)
            meal.save()

            meal_position = MealPosition.objects.create(meal=meal, dish=meal_type_dishes[i], quantity=1)
            meal_position.save()


def _get_random_dishes(dishes: Sequence[Dish], count: int) -> List[Dish]:
    dishes = list(dishes)
    if len(dishes) < count:
        batches_count = math.ceil(count / len(dishes))
        dishes = dishes * batches_count

    return random.sample(dishes, k=count)


def generate_daily_menu_randomly() -> Dict[str, Dish]:
    dishes = Dish.objects.prefetch_related('tags')
    random_menu = {
        'breakfast': random.choice(dishes.filter(tags__name='завтрак')),
        'lunch': random.choice(dishes.filter(tags__name='обед')),
        'dinner': random.choice(dishes.filter(tags__name='ужин')),
    }
    return random_menu


def generate_dates_from_today(days_count: int) -> List[datetime.date]:
    return [
        datetime.date.today() + datetime.timedelta(days=day)
        for day in range(days_count)
    ]


def has_meals(user: User, current_date: datetime.date) -> bool:
    end_date = current_date + datetime.timedelta(days=6)
    return Meal.objects.filter(date__gte=current_date, date__lte=end_date, customer=user).exists()
