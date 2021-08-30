import datetime
import os

from django.template.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from .models import Meal, Dish, MealPosition
from .forms import DaysForm, LoginForm

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from .services import generate_menu_randomly, has_meals


TEMPLATE = os.getenv('TEMPLATE', 'pure_bootstrap')


# def dashboard(request):
#     return render(request, 'dashboard.html', {'section': 'dashboard'})


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


def index_page(request):
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
        total_ingredients.setdefault(ingredient, [0, units, 0])
        total_ingredients[ingredient][0] += quantity
        if total_ingredients[ingredient][2] == 0:
            total_ingredients[ingredient][2] += price
        if units == 'шт':
            total_sum += quantity * price
        elif units == 'г' or units == 'л':
            total_sum += quantity * price / 1000

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
            return render(request, 'register_done.html', {'new_user': new_user})
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
