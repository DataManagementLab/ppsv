import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Course, Student, Group, TopicSelection, Topic, CourseType


class test_ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee')
        cls.group1 = Group.objects.create()
        cls.group1.students.add(cls.student1)
        cls.group1.students.add(cls.student2)
        cls.group1.students.add(cls.student3)
        cls.group2 = Group.objects.create()
        cls.group2.students.add(cls.student1)
        cls.course_type = CourseType.objects.create(type='Testart')
        cls.course = Course.objects.create(registration_deadline=timezone.now(), cp=5, type=cls.course_type)
        cls.topic = Topic.objects.create(course=cls.course, title='Title')
        cls.selection = TopicSelection.objects.create(group=cls.group2, topic=cls.topic)

    def test_error_if_registration_deadline_before_registration_start(self):
        """
        If registration_deadline is before registration_start clean() has to raise a ValidationError
        """
        dtime = timezone.now()
        stime = timezone.now() + datetime.timedelta(days=30)
        dead_course = Course(registration_deadline=dtime, registration_start=stime)
        with self.assertRaises(ValidationError):
            dead_course.clean()

    def test_course_status(self):
        """
        If the registration start of a course lies in the future, the status is upcoming.
        If the current time is between registration start and end, the status is open.
        If the current time is after the registration end, the status is closed.
        If the registration start is within the next 14 days, the status is imminent.
        """
        date_past = timezone.now() - datetime.timedelta(days=30)
        date_future = timezone.now() + datetime.timedelta(days=30)
        date_near_future = timezone.now() + datetime.timedelta(days=13)
        course_open = Course(registration_deadline=date_future, registration_start=date_past)
        self.assertEqual(course_open.get_status, 'Open')
        course_closed = Course(registration_deadline=date_past)
        self.assertEqual(course_closed.get_status, 'Closed')
        course_upcoming = Course(registration_start=date_future)
        self.assertEqual(course_upcoming.get_status, 'Upcoming')
        course_imminent = Course(registration_start=date_near_future)
        self.assertEqual(course_imminent.get_status, 'Imminent')

    def test_get_display(self):
        """
        Tests the get_display method/property of a group.
        """
        self.assertEqual(self.group1.get_display, 'ab12eeee, bc22eeee, cd33eeee')

    def test_group_size(self):
        """
        Test if the group.size property works correctly.
        """
        self.assertEqual(self.group1.size, 3)
        self.assertEqual(self.group2.size, 1)

    def test_group_string_rep(self):
        """
        Tests the string representation of a group.
        """
        self.assertEqual(self.group1.__str__(), 'group 1')

    def test_topic_selection_string_rep(self):
        """
        Tests the string representation of a topic selection.
        """
        self.assertEqual(self.selection.__str__(), 'group 2, Title')

    def test_topic_selection_get_display(self):
        """
        Tests the get_display method/property of a topic selection.
        """
        self.assertEqual(self.selection.get_display, 'ab12eeee')
