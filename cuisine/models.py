from django.db import models
from django.core.validators import MinValueValidator


class Dish(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    recipe = models.TextField(
        'рецепт',
        max_length=2000,
    )
    cooking_time = models.PositiveSmallIntegerField(
        'время готовки',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        'изображение',
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


class Ingridient(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    units = models.CharField(
        'единицы измерения',
        max_length=20,
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return self.name


class IngridientPosition(models.Model):
    ingridient = models.ForeignKey(
        Ingridient,
        verbose_name='ингридиент',
        related_name='позиция',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        'число',
        validators=[MinValueValidator(1)],
    )

    dish = models.ForeignKey(
        Dish,
        verbose_name='блюдо',
        related_name='positions',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'позиция ингридиентов блюда'
        verbose_name_plural = 'позиции ингридиентов блюда'

    def __str__(self):
        return self.ingridient.name


class Meal(models.Model):
    MEAL_TYPE = (
        ('BREAKFAST', 'завтрак'),
        ('LUNCH', 'обед'),
        ('DINNER', 'ужин'),
    )

    meal_type = models.CharField(
        'тип приема пищи',
        max_length=20,
        choices=MEAL_TYPE,
        blank=True,
        db_index=True,
    )
    quantity = models.PositiveSmallIntegerField(
        'число',
        validators=[MinValueValidator(1)],
    )
    date = models.DateField(
        'дата',
        db_index=True,
    )

    class Meta:
        verbose_name = 'прием пищи'
        verbose_name_plural = 'приемы пищи'

    def __str__(self):
        return self.meal_type


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
