# Generated by Django 4.0 on 2022-03-16 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0019_alter_course_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='motivation_text',
            field=models.BooleanField(default=False, verbose_name='motivation texts are required'),
        ),
    ]
