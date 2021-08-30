import datetime
import os
import random

from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import csrf

from cuisine.models import Meal, Dish, MealPosition
from cuisine.forms import DaysForm, LoginForm, UserRegistrationForm


TEMPLATE = os.getenv('TEMPLATE', 'pure_bootstrap')


def get_random_menu():
    dishes = Dish.objects.prefetch_related('tags')
    random_menu = {
        'breakfast': random.choice(dishes.filter(tags__name='завтрак')),
        'lunch': random.choice(dishes.filter(tags__name='обед')),
        'dinner': random.choice(dishes.filter(tags__name='ужин')),
    }
    return random_menu


def index_page(request):
    global saved_random_menu
    if not request.user.is_authenticated:
        context = get_random_menu()
        saved_random_menu = [context['breakfast'].id, context['lunch'].id, context['dinner'].id]
        return render(request, f'{TEMPLATE}/index.html', context)
    else:
        return redirect('week_menu')


def daily_menu(user):
    items = (
        MealPosition.objects
        .filter(meal__date=datetime.date.today(), meal__customer=user)
        .select_related('dish', 'meal')
    )
    context = {item.meal.meal_type.lower(): (item, item.dish.id) for item in items}
    return context


def generate_next_week_menu(user):
    dishes = Dish.objects.prefetch_related('tags')

    local_dishes = {
        'breakfast': list(dishes.filter(tags__name='завтрак')),
        'lunch': list(dishes.filter(tags__name='обед')),
        'dinner': list(dishes.filter(tags__name='ужин')),
    }

    for index, meal_type in enumerate(local_dishes):
        first_day_meal = Meal.objects.create(
            meal_type=meal_type.upper(),
            date=datetime.datetime.today(),
            customer=user)
        MealPosition.objects.create(
            meal=first_day_meal,
            dish=dishes.get(id=saved_random_menu[index]),
            quantity=1)
    for index, dish in enumerate(local_dishes):
        local_dishes[dish].remove(dishes.get(id=saved_random_menu[index]))

    first_date = datetime.datetime.today() + datetime.timedelta(days=1)
    for day in range(6):
        date = first_date + datetime.timedelta(days=day)
        for meal_type in local_dishes:
            meal = Meal.objects.create(
                meal_type=meal_type.upper(),
                date=date,
                customer=user)
            dish = local_dishes[meal_type].pop(random.choice(range(len(local_dishes[meal_type]))))
            MealPosition.objects.create(
                meal=meal,
                dish=dish,
                quantity=1)


def generate_last_day_week_menu(user, needed_generated_menu_days):
    dishes = Dish.objects.prefetch_related('tags')

    local_dishes = {
        'breakfast': list(dishes.filter(tags__name='завтрак')),
        'lunch': list(dishes.filter(tags__name='обед')),
        'dinner': list(dishes.filter(tags__name='ужин')),
    }
    first_date = datetime.datetime.today() + datetime.timedelta(days=needed_generated_menu_days + 1)
    for day in range(7 - needed_generated_menu_days):
        date = first_date + datetime.timedelta(days=day)
        for meal_type in local_dishes:
            meal = Meal.objects.create(
                meal_type=meal_type.upper(),
                date=date,
                customer=user)
            dish = local_dishes[meal_type].pop(random.choice(range(len(local_dishes[meal_type]))))
            MealPosition.objects.create(
                meal=meal,
                dish=dish,
                quantity=1)


def show_next_week_menu(request):
    if not Meal.objects.filter(customer=request.user):
        generate_next_week_menu(request.user)
    last_meal_date = Meal.objects.filter(customer=request.user).last().date
    needed_generated_menu_days = (last_meal_date - datetime.datetime.today().date()).days
    if 0 <= needed_generated_menu_days < 7:
        generate_last_day_week_menu(request.user, needed_generated_menu_days)

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
    if request.method == 'POST':
        form = DaysForm(request.POST)
        if not form.is_valid():
            return render(request, f'{TEMPLATE}/calculator.html')
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
            total_ingredients.setdefault(ingredient, [0, units, 0])
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
        context.update(csrf(request))
        if weekdays:
            context['start_day'] = weekdays[0]
            context['end_day'] = weekdays[-1]
    else:
        form = DaysForm()
        context = {'form': form}

    return render(request, f'{TEMPLATE}/calculator.html', context)


def view_recipe(request, recipe_id):
    dish = get_object_or_404(Dish, pk=recipe_id)
    return render(request, f'{TEMPLATE}/recipe.html', context={'recipe': dish})


def count_days(days_count):
    return [
        datetime.date.today() + datetime.timedelta(days=day)
        for day in range(days_count)
    ]


# def show_daily_menu(request):
#     context = daily_menu(request.user)
#     return render(request, f'{TEMPLATE}/daily_menu.html', context=context)


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
