"""Purpose of this file

This file describes or defines the basic structure of the PPSV.
A class that extends the models.Model class may represent a Model
of the platform and can be registered in admin.py.
"""
from datetime import datetime, time

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _


class CourseType(models.Model):
    """CourseType

    This model represents the types courses can have.

    :attr CourseType.type: The course type
    :type CourseType.type: CharField
    """
    type = models.CharField(max_length=200, verbose_name=_('type'))

    class Meta:
        """Meta options

        This class handles all possible meta options that you can give to this model.

        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("course Type")
        verbose_name_plural = _("course Types")

    def __str__(self):
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.type


class Term(models.Model):
    """A Term
    only on can be active"""
    name = models.CharField(max_length=200, verbose_name=_("title"))
    active_term = models.BooleanField(default=False, verbose_name=_("active term"))
    registration_start = models.DateTimeField(default=make_aware(datetime.combine(datetime.today(), time(23, 59, 59))),
                                              verbose_name=_("registration Start"))
    registration_deadline = models.DateTimeField(
        default=make_aware(datetime.combine(datetime.today(), time(23, 59, 59))),
        verbose_name=_("registration Deadline"))

    class Meta:
        """Meta options

        This class handles all possible meta options that you can give to this model.

        :attr Meta.verbose_name: A human-readable name for the object in singular
        :type Meta.verbose_name: __proxy__
        :attr Meta.verbose_name_plural: A human-readable name for the object in plural
        :type Meta.verbose_name_plural: __proxy__
        """
        verbose_name = _("term")
        verbose_name_plural = _("terms")

    def __str__(self):
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.name

    def clean(self):
        query = Term.objects.filter(active_term=True).exclude(pk=self.pk)
        if query.count() == 1 and self.active_term:
            raise ValidationError("There can be only one active Term")
        if self.registration_start >= self.registration_deadline:
            raise ValidationError(_("The registration deadline cannot be before the registration start."))

    @staticmethod
    def has_active_term():
        return Term.objects.filter(active_term=True).exists()

    @staticmethod
    def get_active_term():
        if not Term.has_active_term():
            return None
        return Term.objects.get(active_term=True)

    @staticmethod
    def get_active_term_registration_start():
        if not Term.has_active_term():
            return None
        return Term.get_active_term().registration_start

    @staticmethod
    def get_active_term_registration_deadline():
        if not Term.has_active_term():
            return None
        return Term.get_active_term().registration_deadline


class Course(models.Model):
    """Course

    This model represents a course on the platform. A course contains a title, a type, a registration start date,
    a registration Deadline, a description, a boolean to set if it is unlimited, the number of maximum participants,
    the CP of the course, a faculty and an organizer.

    :attr Course.title: The title of the course
    :type Course.title: CharField
    :attr Course.type: The type of the course
    :type Course.type: ForeignKey
    :attr Course.registration_start: The start date of the registration
    :type Course.registration_start: DateTimeField
    :attr Course.registration_deadline: The end date of the registration
    :type Course.registration_deadline: DateTimeField
    :attr Course.description: The description of the course
    :type Course.description: TextField
    :attr Course.collection_exclusive: if a user can only choose this course in one collection with one group
    :type Course.collection_exclusive: BooleanField
    :attr Course.unlimited: if the number of participants is unlimited
    :type Course.unlimited: BooleanField
    :attr Course.max_slots: the maximum number of participants
    :type Course.max_slots: IntegerField
    :attr Course.cp: the CP of the Course
    :type Course.cp: IntegerField
    :attr Course.faculty: The faculty of the course
    :type Course.faculty: CharField
    :attr Course.motivation_text: if the course demands motivation texts
    :type Course.motivation_text: BooleanField
    :attr Course.organizer: The organizer of the course
    :type Course.organizer: CharField

    """
    title = models.CharField(max_length=200, verbose_name=_("title"))
    type = models.ForeignKey(CourseType, on_delete=models.CASCADE, verbose_name=_("type"))
    term = models.ForeignKey(Term, on_delete=models.CASCADE, default=Term.get_active_term)
    registration_start = models.DateTimeField(default=Term.get_active_term_registration_start,
                                              verbose_name=_("registration Start"))
    registration_deadline = models.DateTimeField(default=Term.get_active_term_registration_deadline,
                                                 verbose_name=_("registration Deadline"))
    description = models.TextField(verbose_name=_("description"))
    cp = models.IntegerField('CP', validators=[MaxValueValidator(100), MinValueValidator(0)])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

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
    motivation_text = models.BooleanField(_("motivation texts are required"), default=False)

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

    def clean(self):
        """
        Implements base.clean(self)
        raises an error if registration start is set to be after registration deadline
        """
        if self.registration_start >= self.registration_deadline:
            raise ValidationError(_("The registration deadline cannot be before the registration start."))

    def __str__(self):
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.title

    @property
    def get_status(self):
        """String representation
        Returns the registration status (Open,Imminent, Upcoming,Closed).
        :return: the registration status (Open,Imminent, Upcoming,Closed)
        :rtype: str
        """
        if timezone.now() < self.registration_start:
            if (self.registration_start - timezone.now()).days <= 14:
                return "Imminent"
            else:
                return "Upcoming"
        elif self.registration_start < timezone.now() < self.registration_deadline:
            return "Open"
        elif timezone.now() > self.registration_deadline:
            return "Closed"


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course_<id>/<filename>
    return 'course_{0}/{1}'.format(instance.course.id, filename)


class Topic(models.Model):
    """Topic

    This model represents a topic on the platform. A Topic contains a title, the maximum number of slots
    (how many distinct assignments for this topic will be created at most), the min and max size of a topic
    (how many students can work together on the topic) and a description. It can contain a file.

    Multiple topics can be part of one course.

    :attr Topic.title: The title of the topic
    :type Topic.title: CharField
    :attr Topic.description: The description of the topic
    :type Topic.description: TextField
    :attr Topic.max_slots: The maximum number of slots of the topic
    :type Topic.max_slots: IntegerField
    :attr Topic.min_slot_size: The minimum number of a slot
    :type Topic.min_slot_size: PositiveIntegerField
    :attr Topic.max_slot_size: The maximum number of a slot
    :type Topic.max_slot_size: PositiveIntegerField
    :attr Topic.file: A file containing information about the topic
    :type Topic.file: FileField
    :attr Topic.course: The course containing the topic
    :type Topic.course: ForeignKey - Course

    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("course"))
    title = models.CharField(max_length=200, verbose_name=_("title"))
    max_slots = models.PositiveIntegerField(verbose_name=_("max slot count"), default=1,
                                            validators=[MinValueValidator(1)])
    min_slot_size = models.PositiveIntegerField(verbose_name=_("min GroupSize"), default=1,
                                                validators=[MinValueValidator(1)])
    max_slot_size = models.PositiveIntegerField(verbose_name=_("max GroupSize"), default=1,
                                                validators=[MinValueValidator(1)])
    description = models.TextField(verbose_name=_("description"))
    file = models.FileField(verbose_name=_("file"), upload_to=course_directory_path, blank=True)

    @property
    def is_group_topic(self):
        """Is group topic
        :return: true, if multiple studens can work together on this topic
        :rtype: boolean
        """
        return self.max_slot_size > 1

    @property
    def has_applications(self):
        """true if it has at least ona application
        :return: true, if this topic has at least one application
        :rtype: bool
        """
        return TopicSelection.objects.filter(topic=self, topic__course__term=Term.get_active_term()).count() > 0

    def clean(self):
        if self.min_slot_size > self.max_slot_size:
            raise ValidationError("min group size is bigger than max group size")

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
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.title


class Student(models.Model):
    """Student

    This model represents a student on the platform. A student contains a TUCaN-ID, a first name, a last name,
    and an email.

    :attr Student.user: The User of the student
    :type Student.user: User
    :attr Student.tucan_id: The TUCaN-ID of the student
    :type Student.tucan_id: CharField
    :attr Student.firstname: The first name of the student
    :type Student.firstname: CharField
    :attr Student.lastname: The last name of the student
    :type Student.lastname: CharField
    :attr Student.email: The Email of the student
    :type Student.email: EmailField

    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.tucan_id


class Group(models.Model):
    """Group

    This model represents a group on the platform. Multiple students can be part of a group and multiple topics can be
    assigned to a group.

    :attr Group.students: The students in a group
    :type Group.students: ManyToManyField - Student
    :attr Group.applications: The applications of a group
    :type Group.applications: ManyToManyField - Topic
    :property Group.size: The size of a group
    :type Group.size: int

    """
    students = models.ManyToManyField(Student, verbose_name=_("students"))
    collection_count = models.IntegerField(verbose_name=_("number of collections"), default=1)
    term = models.ForeignKey(Term, verbose_name=_("term"), default=Term.get_active_term, on_delete=models.CASCADE)

    @property
    def members(self):
        """members of this group
        :return: a list containing the members of this group
        :rtype: list
        """
        return self.students.all()

    @property
    def size(self):
        """size of the group
        :return: the number of students in the group
        :rtype: int
        """
        if not hasattr(self, 'students'):
            return 0
        studs = self.students
        return studs.count()

    size.fget.short_description = _("group Size")

    @property
    def get_collections(self):
        """collections of this group as dictionary order by top to low priority
        """
        collections = {}
        for application in TopicSelection.objects.filter(group=self,
                                                         topic__course__term=Term.get_active_term()) \
                .order_by("collection_number", "priority"):
            if application.collection_number in collections:
                collections[application.collection_number].append(application)
            else:
                collections[application.collection_number] = [application]
        return collections

    @property
    def get_display(self):
        """String representation
        Returns a list of all students in this object.
        :return: the string representation of this object
        :rtype: str
        """
        if not hasattr(self, 'students'):
            return 'Empty'
        studs = self.students.all()
        return ', '.join(str(stud) for stud in studs)

    get_display.fget.short_description = _("group")

    def __str__(self):
        """String representation
        Returns the the string "group" with the number of the group
        :return: the string representation of this object
        :rtype: str
        """
        return _("group") + " " + str(self.pk)

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
    """Topic Selection

    This model represents a topic selection on the platform. A group can select topics. The topic selection can contain
    a motivational text and contains a priority.

    :attr TopicSelection.group: The group selecting the topic
    :type TopicSelection.group: ForeignKey - Group
    :attr TopicSelection.topic: The selected topic
    :type TopicSelection.topic: ForeignKey - Topic
    :attr TopicSelection.motivation: The motivational text of the group
    :type TopicSelection.motivation: TextField
    :attr TopicSelection.priority: The priority of the selected topic
    :type TopicSelection.priority: IntegerField
    :attr TopicSelection.collection_number: The collection_number of the selected topic
    :type TopicSelection.collection_number: IntegerField

    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_("group"))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name=_("topic"))
    motivation = models.TextField(verbose_name=_("motivation Text"), blank=True)
    priority = models.IntegerField(verbose_name=_("priority"), default=1,
                                   validators=[MaxValueValidator(99), MinValueValidator(1)])
    collection_number = models.IntegerField(verbose_name=_("collection number"), default=1)

    @property
    def dict_key(self):
        return self.group, self.collection_number

    @property
    def get_display(self):
        """String representation
        Returns all members of the group.
        :return: a string representation of this object
        :rtype: str
        """
        if self.group.size == 0:
            return 'Empty'
        studs = self.group.students.all()
        return ', '.join(str(stud) for stud in studs)

    @property
    def get_all_applications_in_collection(self):
        """
        :return: all applications of the group of this application that are in the same collection
        :rtype: QuerySet
        """
        return TopicSelection.objects.filter(group=self.group, collection_number=self.collection_number,
                                             topic__course__term=Term.get_active_term())

    @classmethod
    def get_collection_dict(cls):
        """
        :return: a dict with keys (group, collection_number) and values "list of all applications
        :rtype: QuerySet
         """
        collection_dict = {}
        for group in Group.objects.all():
            for application in cls.objects.filter(group=group, topic__course__term=Term.get_active_term()):
                if (group, application.collection_number) not in collection_dict:
                    collection_dict[(group, application.collection_number)] = []
                collection_dict[(group, application.collection_number)].append(application)
        return collection_dict

    get_display.fget.short_description = _("group")

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

    def __str__(self):
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return '{}, {}, #{}'.format(self.group, self.topic, self.priority)


class TextSaves(models.Model):
    """TextSaves

    This model represents a saved text on the platform. A student can save motivational texts.

    :attr TextSaves.student: The student who saved the text
    :type TextSaves.student: ForeignKey - Student
    :attr TextSaves.topic: The topic for which the text was used
    :type TextSaves.topic: CharField
    :attr TextSaves.motivation: The motivational text of the group
    :type TextSaves.motivation: TextField

    """
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
