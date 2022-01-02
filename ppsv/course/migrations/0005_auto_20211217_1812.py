# Generated by Django 3.2.9 on 2021-12-17 17:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20211214_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='max_participants',
            field=models.IntegerField(default=9999, validators=[django.core.validators.MaxValueValidator(9999), django.core.validators.MinValueValidator(0)], verbose_name='maximum Participants'),
        ),
        migrations.AlterField(
            model_name='course',
            name='unlimited',
            field=models.BooleanField(blank=True, default=False, verbose_name='unlimited Number of Participants'),
        ),
    ]
