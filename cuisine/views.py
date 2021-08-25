import datetime

from django.shortcuts import render


from .models import Meal


def show_next_week_menu(request):
    user_id = 1  #TODO get customer
    weekdays = [
        datetime.date.today() + datetime.timedelta(days=day) for day in range(1, 3)
    ]

    meals = (
        Meal.objects
        .filter(date__in=weekdays)
        .filter(customer=user_id)
        .prefetch_related('meal_positions__dish')
    )

    meals_per_day = ((day, meals.filter(date=day)) for day in weekdays)

    serialized_meals = {}
    for day, daily_serving in meals_per_day:
        daily_dishes = {
            'breakfast': daily_serving.get(meal_type='BREAKFAST'),
            'lunch': daily_serving.get(meal_type='LUNCH'),
            'dinner': daily_serving.get(meal_type='DINNER'),
        }
        serialized_meals.setdefault(day, daily_dishes)

    return render(
        request, 'temp_week_menu.html',
        context={'meals': serialized_meals}
    )


# def calculate_products(request):
