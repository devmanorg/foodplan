import datetime
import random

from django.template.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import Meal, Dish, MealPosition
from .forms import DaysForm, LoginForm

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'section': 'dashboard'})


def get_days(request):
    if request.method == 'POST':
        form = DaysForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('calculator')
    else:
        form = DaysForm()

    context = {'form': form}
    context.update(csrf(request))

    return render(request, 'name.html', context=context)


def index_page(request):
    return render(request, 'index.html')


def show_next_week_menu(request):
    weekdays = count_days(7)
    user_id = 1
    meals = (
        Meal.objects
        .filter(date__in=weekdays)
        .filter(customer=user_id)
        .prefetch_related('meal_positions__dish')
    )

    serialized_meals = {}
    for meal in meals:
        positions = {}
        for position in meal.meal_positions.all():
            positions.setdefault('id', position.dish.id)
            positions.setdefault('dish', position.dish.name)
            positions.setdefault('quantity', position.quantity)
            positions.setdefault('image', position.dish.image)
        meal_type = {meal.get_meal_type_display(): positions}
        serialized_meals.setdefault(meal.date, meal_type)
        serialized_meals[meal.date].update(meal_type)

    return render(
        request,
        'temp_week_menu.html',
        context={'meals': serialized_meals},
    )


def calculate_products(request):
    days_to_calculate = int(request.POST.get('days'), 1)
    weekdays = count_days(days_to_calculate)

    ingredients = (
        Meal.objects
        .filter(date__in=weekdays)
        .values_list(
            'meal_positions__dish__positions__ingredient__name',
            'meal_positions__dish__positions__quantity',
            'meal_positions__dish__positions__ingredient__units',
        )
    )

    total_ingredients = {}
    for ingredient, quantity, units in ingredients:
        total_ingredients.setdefault(ingredient, [0, units])
        total_ingredients[ingredient][0] += quantity

    return render(
        request,
        'temp_calc.html',
        context={'ingredients': total_ingredients},
    )


def view_recipe(request, recipe_id):
    dish = get_object_or_404(Dish, pk=recipe_id)
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


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
