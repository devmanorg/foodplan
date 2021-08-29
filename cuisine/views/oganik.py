import datetime
import os
import random

from django.template.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from cuisine.models import Meal, Dish, MealPosition
from cuisine.forms import DaysForm, LoginForm, DashboardForm

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from cuisine.forms import UserRegistrationForm
from cuisine.services import generate_menu_randomly, has_meals


TEMPLATE = os.getenv('TEMPLATE', 'oganik')
MEAL_TYPE_RU_TO_EN = {'завтрак': 'breakfast', 'обед': 'lunch', 'ужин': 'dinner'}


def dashboard(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            print(form.data)
            return HttpResponseRedirect('dashboard')
    else:
        form = DashboardForm()
    context = {
        'section': 'dashboard',
        'form': form,
    }
    context = {'form': form}
    context.update(csrf(request))
    return render(request, f'{TEMPLATE}/dashboard.html', context=context)


def get_days(request):
    if request.method == 'POST':
        form = DaysForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('calculator')
    else:
        form = DaysForm()

    context = {'form': form}
    context.update(csrf(request))

    return render(request, f'{TEMPLATE}/name.html', context=context)


def create_random_menu():
    dishes = Dish.objects.prefetch_related('tags')
    menu_items = [
        {
            'dish_id': dish.id,
            'dish_name': dish.name,
            'image_url': dish.image.url,
            'meal_type_ru': meal_type.capitalize(),
            'meal_type_en': MEAL_TYPE_RU_TO_EN[meal_type],
        }
        for meal_type, count in [('завтрак', 2), ('обед', 3), ('ужин', 2)]
        for dish in random.choices(dishes.filter(tags__name=meal_type), k=count)
    ]
    return menu_items


def index_page(request):
    if not request.user.is_authenticated:
        return render(request, f'{TEMPLATE}/index.html', context={'menu_items': create_random_menu()})
    else:
        context = {'has_meals': has_meals(user=request.user, current_date=datetime.date.today())}
        return render(request, f'{TEMPLATE}/index.html', context)


def show_next_week_menu(request):
    weekdays = count_days(7)
    meals = (
        Meal.objects
        .select_related('customer')
        .filter(date__in=weekdays, customer=request.user)
        .order_by('date')
        .prefetch_related('meal_positions__dish')
    )
    serialized_meals = {}
    for meal in meals:
        positions = {}
        for position in meal.meal_positions.all():
            positions.setdefault('id', position.dish.id)
            positions.setdefault('dish', position.dish.name)
            positions.setdefault('meal_type', position)
            positions.setdefault('quantity', position.quantity)
            positions.setdefault('image', position.dish.image)
        meal_type = {meal.get_meal_type_display(): positions}
        serialized_meals.setdefault(meal.date, meal_type)
        serialized_meals[meal.date].update(meal_type)

    return render(request, f'{TEMPLATE}/week_menu.html', context={'meals': serialized_meals})


def calculate_products(request):
    form = DaysForm()
    days_to_calculate = int(request.POST.get('days', 0))
    weekdays = count_days(days_to_calculate)

    ingredients = (
        Meal.objects
        .filter(date__in=weekdays, customer=request.user)
        .values_list(
            'meal_positions__dish__positions__ingredient__name',
            'meal_positions__dish__positions__quantity',
            'meal_positions__dish__positions__ingredient__units',
            'meal_positions__dish__positions__ingredient__price',
        )
    )

    total_ingredients = {}
    total_sum = 0
    for ingredient, quantity, units, price in ingredients:
        if price is None:
            price = 0
        # ingredient_info = {
        #     'quantity': quantity,
        #     'units': units,
        #     'total_price': 0,
        # }
        total_ingredients.setdefault(ingredient, [0, units, 0])
        # total_ingredient_price = ingredient['quantity'] * ingredient['price']
        # if units == 'г' or units == 'мл':
        #     total_ingredient_price /= 1000
        # ingredient['quantity'] += ingredient_info['quantity']
        # ingredient['total_price'] += total_ingredient_price

        total_ingredients[ingredient][0] += float(f'{quantity:.2f}')
        ingredient_price = quantity * int(price)
        if units == 'г' or units == 'мл':
            ingredient_price = quantity * int(price) / 1000
        total_ingredients[ingredient][2] += float(f'{ingredient_price:.2f}')
        total_sum += ingredient_price

    context = {
        'ingredients': total_ingredients, 'form': form,
        'total_sum': round(total_sum)
    }
    if weekdays:
        context['start_day'] = weekdays[0]
        context['end_day'] = weekdays[-1]

    return render(request, f'{TEMPLATE}/calculator.html', context)


def view_recipe(request, recipe_id):
    dish = get_object_or_404(Dish, pk=recipe_id)
    return render(request, f'{TEMPLATE}/recipe.html', context={'recipe': dish})


def count_days(days_count):
    return [
        datetime.date.today() + datetime.timedelta(days=day)
        for day in range(days_count)
    ]


def show_daily_menu(request):
    items = (
        MealPosition.objects
        .filter(meal__date=datetime.date.today(), meal__customer=request.user)
        .select_related('dish', 'meal')
    )
    context = {item.meal.meal_type.lower(): (item, item.dish.id) for item in items}
    return render(request, f'{TEMPLATE}/daily_menu.html', context=context)


def register(request):
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


def user_login(request):
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


def generate_menu(request):
    is_generated = generate_menu_randomly(user=request.user, current_dt=datetime.datetime.now())
    if is_generated:
        return redirect('week_menu')
    else:
        return redirect('index')
