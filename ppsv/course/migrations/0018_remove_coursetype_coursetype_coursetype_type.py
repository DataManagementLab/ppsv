# Generated by Django 4.0 on 2022-03-15 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0017_alter_course_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursetype',
            name='coursetype',
        ),
        migrations.AddField(
            model_name='coursetype',
            name='type',
            field=models.CharField(default='Seminar', max_length=200, verbose_name='type'),
            preserve_default=False,
        ),
    ]
