# Generated by Django 3.2.6 on 2021-08-29 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuisine', '0007_auto_20210826_0100'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='цена за кг/л/шт'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='cooking_time',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='время готовки'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='units',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='единицы измерения'),
        ),
        migrations.AlterField(
            model_name='ingredientposition',
            name='quantity',
            field=models.FloatField(verbose_name='число'),
        ),
    ]
