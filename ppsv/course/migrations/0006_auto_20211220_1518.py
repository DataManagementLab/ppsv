# Generated by Django 3.2.9 on 2021-12-20 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_auto_20211217_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='size',
        ),
        migrations.AlterField(
            model_name='topicselection',
            name='motivation',
            field=models.TextField(blank=True, verbose_name='motivation Text'),
        ),
    ]