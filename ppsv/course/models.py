import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200)

    # maybe we need more choices
    SEMINAR = 'SE'
    PRAKTIKUM = 'PR'
    COURSE_TYPE_CHOICES = [
        (SEMINAR, 'Seminar'),
        (PRAKTIKUM, 'Praktikum'),
    ]
    type = models.CharField(max_length=2, choices=COURSE_TYPE_CHOICES, default=SEMINAR)

    registration_start = models.DateTimeField('date registration starts', default=timezone.now)
    registration_deadline = models.DateTimeField('registration deadline')
    description = models.TextField('course description')
    max_participants = models.IntegerField('maximum number of participants', default=9999,
                                           validators=[MaxValueValidator(9999), MinValueValidator(0)])
    cp = models.IntegerField('CP', validators=[MaxValueValidator(100), MinValueValidator(0)])
    # maybe we need more choices
    OBLIGATORY = 'PF'
    OPTIONAL = 'WA'
    COURSE_CATEGORY_CHOICES = [
        (OBLIGATORY, 'obligatory'),
        (OPTIONAL, 'optional'),
    ]
    category = models.CharField(max_length=2, choices=COURSE_CATEGORY_CHOICES, default=OPTIONAL)

    # maybe we need more choices
    INFORMATIK = 'FB20'
    PHYSIK = 'FB05'
    COURSE_FACULTY_CHOICES = [
        (INFORMATIK, 'FB20 Informatik'),
        (PHYSIK, 'FB05 PHYSIK'),
    ]
    faculty = models.CharField(max_length=4, choices=COURSE_FACULTY_CHOICES)

    # organizer or instructors?
    organizer = models.CharField(max_length=200)

    def __str__(self):
        return self.name


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course_<id>/<filename>
    return 'course_{0}/{1}'.format(instance.course.id, filename)


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    max_participants = models.IntegerField('maximum number of participants', default=9999,
                                           validators=[MaxValueValidator(9999), MinValueValidator(0)])
    description = models.TextField('topic description')
    file = models.FileField(upload_to='course_directory_path', blank=True)

    def __str__(self):
        return self.title


class Student(models.Model):
    tucan_id = models.CharField(max_length=8, primary_key=True)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.tucan_id


class Group(models.Model):
    students = models.ManyToManyField(Student)
    size = models.IntegerField('size of group', default=1, validators=[MaxValueValidator(99), MinValueValidator(1)])
    assignments = models.ManyToManyField(Topic, blank=True)


class TopicSelection(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    motivation = models.TextField('motivation text')
    priority = models.IntegerField('priority', default=1,
                                   validators=[MaxValueValidator(99), MinValueValidator(1)])


class TextSaves(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    motivation = models.TextField('motivation text')

