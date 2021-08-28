import logging
import random
import datetime

from django.contrib.auth.models import User

from cuisine.models import MealPosition, Dish, Meal

logger = logging.getLogger(__name__)


_MEAL_TYPE_TO_TAGS = {
    'BREAKFAST': ['Завтраки', 'Выпечка и десерты', 'Сэндвичи'],
    'LUNCH': ['Супы', 'Бульоны', 'Основные блюда'],
    'DINNER': ['Основные блюда', 'Салаты', 'Паста и пицца'],
}


def generate_menu_randomly(user: User, current_dt: datetime.datetime) -> bool:
    logger.info('Hello')
    if has_meals(user, current_dt.date()):
        logger.info('return False')
        return False

    generate_meal_for_current_day(current_dt, user)
    generate_meal_for_next_days(current_dt.date(), user, days_count=6)
    return True


def has_meals(user: User, current_date: datetime.date) -> bool:
    end_date = current_date + datetime.timedelta(days=6)
    return Meal.objects.filter(date__gte=current_date, date__lte=end_date, customer=user).exists()


def generate_meal_for_current_day(current_dt: datetime.datetime, user: User):
    logger.info('start generate_meal_for_current_day')
    logger.info(f'{current_dt.time().hour=}')
    for max_hour, meal_type in [(10, 'BREAKFAST'), (16, 'LUNCH'), (24, 'DINNER')]:
        if current_dt.time().hour >= max_hour:
            continue
        generate_meal_randomly(current_dt.date(), user, meal_type)


def generate_meal_for_next_days(current_date: datetime.date, user: User, days_count: int):
    logger.info('start generate_meal_for_next_days')

    for day in range(1, days_count + 1):
        date = current_date + datetime.timedelta(days=day)
        generate_meal_randomly(date, user, meal_type='BREAKFAST')
        generate_meal_randomly(date, user, meal_type='LUNCH')
        generate_meal_randomly(date, user, meal_type='DINNER')


def generate_meal_randomly(date: datetime.date, user: User, meal_type: str):
    meal = Meal.objects.create(meal_type=meal_type, date=date, customer=user)
    meal.save()

    tags = _MEAL_TYPE_TO_TAGS[meal_type]
    dishes = []
    for dish in Dish.objects.all():
        if dish.tags.filter(name__in=tags).exists():
            dishes.append(dish)

    meal_position = MealPosition.objects.create(meal=meal, dish=random.choice(dishes), quantity=1)
    meal_position.save()
