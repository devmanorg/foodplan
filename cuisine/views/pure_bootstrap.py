import logging
import os
from collections import defaultdict

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import csrf

from cuisine.models import Meal, Dish
from cuisine.forms import DaysForm, LoginForm, UserRegistrationForm
from cuisine.services import (
    generate_dates_from_today,
    generate_daily_menu_randomly,
    regenerate_and_save_menu,
    aggregate_ingredients,
)

TEMPLATE = os.getenv('TEMPLATE', 'pure_bootstrap')
logger = logging.getLogger(__name__)


def index_page(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        context = generate_daily_menu_randomly()
        return render(request, f'{TEMPLATE}/index.html', context)
    else:
        return redirect('week_menu')


def show_next_week_menu(request: HttpRequest) -> HttpResponse:
    regenerate_and_save_menu(request.user)

    weekdays = generate_dates_from_today(days_count=7)
    meals = (
        Meal.objects
        .select_related('customer')
        .filter(date__in=weekdays, customer=request.user)
        .order_by('date')
        .prefetch_related('meal_positions__dish')
    )

    serialized_meals = defaultdict(list)
    for meal in meals:
        dish = meal.meal_positions.first().dish
        serialized_meal = {
            'id': dish.id, 'name': dish.name, 'image_url': dish.image.url, 'meal_type': meal.get_meal_type_display(),
        }
        serialized_meals[meal.date].append(serialized_meal)

    return render(request, f'{TEMPLATE}/week_menu.html', context={'meals': serialized_meals.items()})


def calculate_products(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = DaysForm(request.POST)
        if not form.is_valid():
            return render(request, f'{TEMPLATE}/calculator.html')

        weekdays = generate_dates_from_today(days_count=int(request.POST.get('days', 0)))
        aggregated_ingredients = aggregate_ingredients(request.user, weekdays)

        context = {
            'ingredients': aggregated_ingredients,
            'form': form,
            'total_price': sum(ingredient['total_price'] for ingredient in aggregated_ingredients),
        }
        context.update(csrf(request))
        if weekdays:
            context['start_day'] = weekdays[0]
            context['end_day'] = weekdays[-1]
    else:
        form = DaysForm()
        context = {'form': form}

    return render(request, f'{TEMPLATE}/calculator.html', context)


def view_recipe(request: HttpRequest, recipe_id: int) -> HttpResponse:
    dish = get_object_or_404(Dish, pk=recipe_id)
    return render(request, f'{TEMPLATE}/recipe.html', context={'recipe': dish})


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, f'{TEMPLATE}/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, f'{TEMPLATE}/register.html', {'user_form': user_form})


def user_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, f'{TEMPLATE}/registration/login.html', {'form': form})
