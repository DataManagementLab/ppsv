"""Purpose of this file

This file describes or defines the basic structure of the PPSV.
A class that extends the models.Model class may represent a Model
of the platform and can be registered in admin.py.
"""
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    """Course

    This model represents a course on the platform. A course contains a title, a type, a registration start date,
    a registration Deadline, a description, a boolean to set if it is unlimited, the number of maximum participants,
    the CP of the course, a faculty and an organizer.

    :attr Course.title: The title of the course
    :type Course.title: CharField
    :attr Course.type: The type of the course
    :type Course.type: CharField
    :attr Course.registration_start: The start date of the registration
    :type Course.registration_start: DateTimeField
    :attr Course.registration_deadline: The end date of the registration
    :type Course.registration_deadline: DateTimeField
    :attr Course.description: The description of the course
    :type Course.description: TextField
    :attr Course.unlimited: if the number of participants is unlimited
    :type Course.unlimited: BooleanField
    :attr Course.max_participants: the maximum number of participants
    :type Course.max_participants: IntegerField
    :attr Course.cp: the CP of the Course
    :type Course.cp: IntegerField
    :attr Course.type: The faculty of the course
    :type Course.type: CharField
    :attr Course.type: The organizer of the course
    :type Course.type: CharField

    """
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

    unlimited = models.BooleanField('unlimited Number of Participants', blank=True, default=False)
    max_participants = models.IntegerField(verbose_name=_("maximum Participants"), default=9999,
                                           validators=[MaxValueValidator(9999), MinValueValidator(0)],)

    cp = models.IntegerField('CP', validators=[MaxValueValidator(100), MinValueValidator(0)])

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
        """String representation
        Returns the string representation of this object.
        :return: the string representation of this object
        :rtype: str
        """
        return self.title


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course_<id>/<filename>
    return 'course_{0}/{1}'.format(instance.course.id, filename)


class Topic(models.Model):
    """Topic

    This model represents a topic on the platform. A Topic contains a title, the maximum number of participants and a
    description. It can contain a file.

    Multiple topics can be part of one course.

    :attr Topic.title: The title of the topic
    :type Topic.title: CharField
    :attr Topic.description: The description of the topic
    :type Topic.description: TextField
    :attr Topic.max_participants: The maximum number of participants
    :type Topic.max_participants: IntegerField
    :attr Topic.file: A file containing information about the topic
    :type Topic.file: FileField
    :attr Topic.course: The course containing the topic
    :type Topic.course: ForeignKey - Course

    """
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

    :attr Student.tucan_id: The TUCaN-ID of the student
    :type Student.tucan_id: CharField
    :attr Student.firstname: The first name of the student
    :type Student.firstname: CharField
    :attr Student.lastname: The last name of the student
    :type Student.lastname: CharField
    :attr Student.email: The Email of the student
    :type Student.email: EmailField

    """
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
    :attr Group.assignments: The assignments of a group
    :type Group.assignments: ManyToManyField - Topic
    :property Group.size: The size of a group
    :type Group.size: int
    :property Group.size: The tucan_id of the students separated with commas
    :type Group.get_display: str
    """
    students = models.ManyToManyField(Student, verbose_name=_("students"))
    assignments = models.ManyToManyField(Topic, verbose_name=_("topics"), blank=True)

    # instead of this model we now us a Property for group size
    # size = models.IntegerField(verbose_name=_("group Size"), default=1,
    #                           validators=[MaxValueValidator(99), MinValueValidator(1)])
    @property
    def size(self):
        """size of the group
        :return: the number of students in the group
        :rtype: int
        """
        if not hasattr(self, 'students'):
            return 0
        stu = self.students
        return stu.count()

    size.fget.short_description = _("group Size")

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

    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_("group"))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name=_("topic"))
    motivation = models.TextField(verbose_name=_("motivation Text"), blank=True)
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
