# Generated by Django 4.1.5 on 2023-04-24 19:09

from django.db import migrations


def forwards_func(apps, schema_editor):
    TopicSelection = apps.get_model("base", "TopicSelection")
    for ts in TopicSelection.objects.all():
        ts.priority += 1
        ts.save()


def reverse_func(apps, schema_editor):
    TopicSelection = apps.get_model("base", "TopicSelection")
    for ts in TopicSelection.objects.all():
        ts.priority -= 1
        ts.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_multiple_instructors'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]