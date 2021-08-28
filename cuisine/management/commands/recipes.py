import json
import os
import requests

from bs4 import BeautifulSoup

from requests.exceptions import HTTPError
from urllib.parse import urlsplit
from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from cuisine.models import Dish, Tag, IngredientPosition, Ingredient


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()

    html_doc = response.text
    return BeautifulSoup(html_doc, 'html.parser')


def parse_recipe(url):
    soup = get_soup(url)

    try:
        image_url = soup.select_one('.css-17zastc .css-3uhzwz-ImageBase img').get('src')
    except AttributeError:
        return None

    units_factor = {
        'стол': 20,
        'чай': 10,
        'стакан': 200,
        'по вкусу': 0,
        'кг': 1000,
    }

    name = soup.h1.text.replace('\xa0', ' ')
    tags = list(soup.find(class_='css-a90bfp').stripped_strings)

    ingredients = [ingredient.text for ingredient in soup.find_all(class_='css-12s4kyf-Info')]

    portion_and_time = list(soup.find(class_='css-1k7lmq6').stripped_strings)
    portions = portion_and_time[1]
    cooking_time = portion_and_time[-1]

    quantities = []
    for layout in soup.find_all(class_='css-1t5teuh-Info'):
        quantity = 0
        quantity_with_units = layout.text
        units = quantity_with_units
        digits = list(filter(str.isdigit, quantity_with_units))
        if digits:
            quantity = int(''.join(digits))
            units = quantity_with_units.replace(str(quantity), '').strip()

            if '/' in quantity_with_units:
                quantity = int(digits[0]) / int(''.join(digits[1:]))
                units = quantity_with_units.replace('/'.join(digits), '').strip()
            elif '.' in quantity_with_units:
                quantity = int('.'.join(digits[1:]))
                units = quantity_with_units.replace(quantity, '').strip()
        
        for unit in units_factor:
            if unit in units:
                quantity *= units_factor[unit]
                units = ''
                break
        quantity /= int(portions)
        quantities.append((quantity, units))

    ingredients_and_quantity = dict(zip(ingredients, quantities))

    recipe_steps = [step.text for step in soup.find_all(class_='css-8repvw-Info')]
    recipe = '\n'.join(recipe_steps).replace('\xa0', ' ')

    dish_recipe = {
        'name': name,
        'tags': tags,
        'ingredients_and_quantity': ingredients_and_quantity,
        'cooking_time': cooking_time,
        'recipe': recipe,
        'image': image_url,
    }
    return dish_recipe


@transaction.atomic
def record_recipe(recipe):
    dish, created = Dish.objects.get_or_create(name=recipe['name'])
    if not created:
        return None
    dish.name = recipe['name']
    dish.cooking_time = recipe['cooking_time']
    dish.recipe = recipe['recipe']

    tags = [Tag.objects.get_or_create(name=tag)[0] for tag in recipe['tags']]
    dish.tags.add(*tags)

    for ingredient, quantity_with_units in recipe['ingredients_and_quantity'].items():
        quantity, units = quantity_with_units

        ingredient_model, created = Ingredient.objects.get_or_create(name=ingredient)
        if created and units:
            ingredient_model.units = str(units)
        ingredient_model.save()

        position = IngredientPosition.objects.get_or_create(
            ingredient=ingredient_model, quantity=int(quantity), dish=dish,
        )

    download_image(recipe['image'], dish)


def download_image(url, dish):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_content = ContentFile(response.content)
    except ConnectionError:
        raise CommandError('ConnectionError. Try again later')
    except HTTPError:
        raise CommandError(f'Photo from {url} is not found')
    image_name = os.path.split(urlsplit(url).path)[-1]
    Path(os.path.join(settings.BASE_DIR, 'media')).mkdir(exist_ok=True)
    if image_name not in os.listdir(settings.MEDIA_ROOT):

        dish.image.save(image_name, image_content, save=True)


def fill_recipes_json():
    recipes = []
    for number in range(14444, 14545):
        url = f'https://eda.ru/recepty/supy/sirnij-sup-po-francuzski-s-kuricej-{number}'
        if recipe := parse_recipe(url):
            recipes.append(recipe)
            # print(recipe)

    return recipes


def get_recipes_json_file(recipes):
    print(recipes)
    with open('recipes.json', 'w', encoding='utf-8') as file:
        json.dump(recipes, file, ensure_ascii=False, indent=4)


def read_json():
    with open('recipes.json', 'r', encoding='utf-8') as file:
        return json.load(file)


class Command(BaseCommand):
    help = 'Upload images from .json file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--parse',
            nargs='?',
            default=False,
            type=bool,
            help='Парсит рецепты с eda.ru',
        )
        parser.add_argument(
            '--create',
            default=False,
            type=bool,
            nargs='?',
            help='Записывает файлы из полученного json'
        )

    def handle(self, *args, **options):
        print(options)
        if options.get('parse'):
            recipes = fill_recipes_json()
            # print(recipes)
            get_recipes_json_file(recipes)
        elif options['create']:
            recipes = read_json()
            for recipe in recipes:
                record_recipe(recipe)

