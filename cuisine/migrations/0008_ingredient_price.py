# Generated by Django 3.2.6 on 2021-08-28 14:04

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
    ]
