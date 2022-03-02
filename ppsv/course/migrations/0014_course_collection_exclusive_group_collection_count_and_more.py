# Generated by Django 4.0 on 2022-02-18 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0013_merge_20220131_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='collection_exclusive',
            field=models.BooleanField(blank=True, default=False, verbose_name='collection exclusive'),
        ),
        migrations.AddField(
            model_name='group',
            name='collection_count',
            field=models.IntegerField(default=1, verbose_name='number of collections'),
        ),
        migrations.AddField(
            model_name='topicselection',
            name='collection_number',
            field=models.IntegerField(default=1, verbose_name='collection Number'),
        ),
    ]