import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Course, Student, Group
from django.urls import reverse


class CourseModelTests(TestCase):
    def test_error_if_registration_deadline_before_registration_start(self):
        """
        if registration_deadline is before registration_start clean() has to raise a ValidationError
        """
        dtime = timezone.now()
        stime = timezone.now() + datetime.timedelta(days=30)
        dead_course = Course(registration_deadline=dtime, registration_start=stime)
        with self.assertRaises(ValidationError):
            dead_course.clean()


# only as an example
class CourseIndexViewTests(TestCase):
    def test_page_response(self):
        """
        check response
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the course view.")


class GroupModelTests(TestCase):
    def test_group_size(self):
        """
        Test if the group.size property works correctly
        """
        self.user1 = User.objects.create_user(username='testuser1', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.user3 = User.objects.create_user(username='testuser3', password='12345')
        self.student1 = Student.objects.create(user=self.user1, tucan_id='ab12eeee')
        self.student2 = Student.objects.create(user=self.user2, tucan_id='bc22eeee')
        self.student3 = Student.objects.create(user=self.user3, tucan_id='cd33eeee')
        self.sts = [self.student1, self.student2, self.student3]
        self.group = Group.objects.create()
        self.assertEqual(self.group.size, 0)
        self.group.students.add(self.student1)
        self.assertEqual(self.group.size, 1)
        self.group.students.add(self.student2)
        self.group.students.add(self.student3)
        self.assertEqual(self.group.size, self.sts.__len__())

