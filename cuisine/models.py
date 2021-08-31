from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Dish(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    recipe = models.TextField(
        'рецепт',
        max_length=2000,
    )
    cooking_time = models.CharField(
        'время готовки',
        blank=True,
        null=True,
        max_length=20,
    )
    image = models.ImageField(
        'изображение',
        upload_to='images/'
    )

    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'блюда'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    dishes = models.ManyToManyField(
        Dish,
        related_name='tags',
        verbose_name='блюда',
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    price = models.DecimalField(
        'цена за кг/л/шт',
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    units = models.CharField(
        'единицы измерения',
        max_length=20,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class IngredientPosition(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        related_name='positions',
        on_delete=models.CASCADE,
    )
    quantity = models.FloatField(
        'число',
    )

    dish = models.ForeignKey(
        Dish,
        verbose_name='блюдо',
        related_name='positions',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'позиция ингредиентов блюда'
        verbose_name_plural = 'позиции ингредиентов блюда'

    def __str__(self):
        return self.ingredient.name


class Meal(models.Model):
    MEAL_TYPES = (
        ('BREAKFAST', 'завтрак'),
        ('LUNCH', 'обед'),
        ('DINNER', 'ужин'),
    )

    meal_type = models.CharField(
        'тип приема пищи',
        max_length=20,
        choices=MEAL_TYPES,
        blank=True,
        db_index=True,
    )
    date = models.DateField(
        'дата',
        db_index=True,
    )
    customer = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='meals',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'прием пищи'
        verbose_name_plural = 'приемы пищи'

    def __str__(self):
        return f'{self.get_meal_type_display().title()} {self.date} {self.customer.username}'


class MealPosition(models.Model):
    meal = models.ForeignKey(
        Meal,
        verbose_name='прием пищи',
        related_name='meal_positions',
        on_delete=models.CASCADE,
    )

    dish = models.ForeignKey(
        Dish,
        verbose_name='блюдо',
        related_name='dish_positions',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        'число блюд',
        validators=[MinValueValidator(1)],
        default=1,
    )

    class Meta:
        verbose_name = 'позиция приема пищи'
        verbose_name_plural = 'позиции приема пищи'

    def __str__(self):
        return self.dish.name
