# Generated by Django 3.2.9 on 2021-12-02 11:53

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('course', '0001_initial'), ('course', '0002_auto_20211202_1147'), ('course', '0003_alter_course_registration_start'), ('course', '0004_alter_course_registration_start'), ('course', '0005_alter_course_registration_start'), ('course', '0006_alter_course_registration_start'), ('course', '0007_alter_course_registration_start'), ('course', '0008_alter_topicselection_priority'), ('course', '0009_auto_20211202_1244')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('registration_deadline', models.DateTimeField(verbose_name='registration deadline')),
                ('description', models.TextField(verbose_name='course description')),
                ('max_participants', models.IntegerField(default=9999, validators=[django.core.validators.MaxValueValidator(9999), django.core.validators.MinValueValidator(0)], verbose_name='maximum number of participants')),
                ('cp', models.IntegerField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], verbose_name='CP')),
                ('category', models.CharField(choices=[('PF', 'obligatory'), ('WA', 'optional')], default='WA', max_length=2)),
                ('faculty', models.CharField(choices=[('FB20', 'FB20 Informatik'), ('FB05', 'FB05 PHYSIK')], max_length=4)),
                ('organizer', models.CharField(max_length=200)),
                ('registration_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date registration starts')),
                ('type', models.CharField(choices=[('SE', 'Seminar'), ('PR', 'Praktikum')], default='SE', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('tucan_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=200)),
                ('lastname', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('max_participants', models.IntegerField(default=9999, validators=[django.core.validators.MaxValueValidator(9999), django.core.validators.MinValueValidator(0)], verbose_name='maximum number of participants')),
                ('description', models.TextField(verbose_name='topic description')),
                ('file', models.FileField(blank=True, upload_to='course_directory_path')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
            ],
        ),
        migrations.CreateModel(
            name='TextSaves',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('motivation', models.TextField(verbose_name='motivation text')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.student')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(99), django.core.validators.MinValueValidator(1)], verbose_name='size of group')),
                ('assignments', models.ManyToManyField(blank=True, to='course.Topic')),
                ('students', models.ManyToManyField(to='course.Student')),
            ],
        ),
        migrations.CreateModel(
            name='TopicSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivation', models.TextField(verbose_name='motivation text')),
                ('priority', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(99), django.core.validators.MinValueValidator(1)], verbose_name='priority')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.group')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.topic')),
            ],
        ),
    ]
