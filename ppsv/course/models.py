import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))

    COURSE_TYPE_CHOICES = [
        ('SE', 'Seminar'),
        ('PR', _('Internship')),
        ('SO', _('Miscellaneous')),
    ]
    type = models.CharField(max_length=2, choices=COURSE_TYPE_CHOICES, default='SE', verbose_name=_("type"))

    registration_start = models.DateTimeField(default=timezone.now, verbose_name=_("registration Start"))
    registration_deadline = models.DateTimeField(verbose_name=_("registration Deadline"))
    description = models.TextField(verbose_name=_("description"))
    max_participants = models.IntegerField(verbose_name=_("maximum Participants"), default=9999,
                                           validators=[MaxValueValidator(9999), MinValueValidator(0)])
    cp = models.IntegerField('CP', validators=[MaxValueValidator(100), MinValueValidator(0)])
    # maybe we need more choices
    # OBLIGATORY = 'PF'
    # OPTIONAL = 'WA'
    # COURSE_CATEGORY_CHOICES = [
    #     (OBLIGATORY, 'obligatory'),
    #     (OPTIONAL, 'optional'),
    # ]
    # category = models.CharField(max_length=2, choices=COURSE_CATEGORY_CHOICES, default=OPTIONAL,
    #                             verbose_name=_("category"))

    # maybe we need more choices
    # LAW_AND_ECONOMICS = 'FB01'
    # HISTORY_AND_SOCIAL_SCIENCES = 'FB02'
    # HUMAN_SCIENCES = 'FB03'
    # MATHEMATICS = 'FB04'
    # PHYSICS = 'FB05'
    # CHEMISTRY = 'FB07'
    # BIOLOGY = 'FB10'
    # MATERIALS_AND_EARTH_SCIENCES = 'FB11'
    # CIVIL_AND_ENVIRONMENTAL_ENGINEERING = 'FB13'
    # ARCHITECTURE = 'FB15'
    # MECHANICAL_ENGINEERING = 'FB16'
    # ELECTRICAL_ENGINEERING_AND_INFORMATION_TECHNOLOGY = 'FB18'
    # COMPUTER_SCIENCE = 'FB20'
    COURSE_FACULTY_CHOICES = [
        ('FB01', _('Dept. 01 - Law and Economics')),
        ('FB02', _('Dept. 02 - History and Social Sciences')),
        ('FB03', _('Dept. 03 - Human Sciences')),
        ('FB04', _('Dept. 04 - Mathematics')),
        ('FB05', _('Dept. 05 – Physics')),
        ('FB07', _('Dept. 07 - Chemistry')),
        ('FB10', _('Dept. 10 - Biology')),
        ('FB11', _('Dept. 11 - Materials and Earth Sciences')),
        ('FB13', _('Dept. 13 - Civil and Environmental Engineering')),
        ('FB15', _('Dept. 15 - Architecture')),
        ('FB16', _('Dept. 16 - Mechanical Engineering')),
        ('FB18', _('Dept. 18 - Electrical Engineering and Information Technology')),
        ('FB20', _('Dept. 20 - Computer Science')),
    ]
    faculty = models.CharField(max_length=4, choices=COURSE_FACULTY_CHOICES, verbose_name=_("faculty"))

    # organizer or instructors?
    organizer = models.CharField(max_length=200, verbose_name=_("organizer"))

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course_<id>/<filename>
    return 'course_{0}/{1}'.format(instance.course.id, filename)


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("course"))
    title = models.CharField(max_length=200, verbose_name=_("title"))
    max_participants = models.IntegerField(verbose_name=_("maximum Participants"), default=9999,
                                           validators=[MaxValueValidator(9999), MinValueValidator(0)])
    description = models.TextField(verbose_name=_("description"))
    file = models.FileField(verbose_name=_("file"), upload_to='course_directory_path', blank=True)

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    def __str__(self):
        return self.title


class Student(models.Model):
    tucan_id = models.CharField(max_length=8, primary_key=True, verbose_name=_("student ID"))
    firstname = models.CharField(max_length=200, verbose_name=_("first Name"))
    lastname = models.CharField(max_length=200, verbose_name=_("last Name"))
    email = models.EmailField()

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("student")
        verbose_name_plural = _("students")

    def __str__(self):
        return self.tucan_id


class Group(models.Model):
    # adding this as a primary key would require DB reset
    # group_nr = models.IntegerField(primary_key=True, verbose_name=_("group Nr"))
    students = models.ManyToManyField(Student, verbose_name=_("students"))
    size = models.IntegerField(verbose_name=_("group Size"), default=1,
                               validators=[MaxValueValidator(99), MinValueValidator(1)])
    assignments = models.ManyToManyField(Topic, verbose_name=_("topics"), blank=True)

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("group")
        verbose_name_plural = _("groups")


class TopicSelection(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_("group"))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name=_("topic"))
    motivation = models.TextField(verbose_name=_("motivation Text"))
    priority = models.IntegerField(verbose_name=_("priority"), default=1,
                                   validators=[MaxValueValidator(99), MinValueValidator(1)])

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("topic Selection")
        verbose_name_plural = _("topic Selections")


class TextSaves(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_("student"))
    topic = models.CharField(max_length=200, verbose_name=_("topic"))
    motivation = models.TextField(verbose_name=_("motivation Text"))

    class Meta:
        """Meta options
        This class handles all possible meta options that you can give to this model.
        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("text Save")
        verbose_name_plural = _("text Saves")
