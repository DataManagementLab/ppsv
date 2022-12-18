from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from course.models import Topic, Group, CourseType, Course, Student, TopicSelection
from .models import Assignment


class TestAssignmentModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.superuser = User.objects.create_superuser(username='testsuperuser', password='12345')

        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.user4 = User.objects.create_user(username='testuser4', password='12345')
        cls.user5 = User.objects.create_user(username='testuser5', password='12345')
        cls.user6 = User.objects.create_user(username='testuser6', password='12345')
        cls.user7 = User.objects.create_user(username='testuser7', password='12345')
        cls.user8 = User.objects.create_user(username='testuser8', password='12345')
        cls.user9 = User.objects.create_user(username='testuser9', password='12345')

        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee')
        cls.student4 = Student.objects.create(user=cls.user4, tucan_id='ab13eeee')
        cls.student5 = Student.objects.create(user=cls.user5, tucan_id='bc23eeee')
        cls.student6 = Student.objects.create(user=cls.user6, tucan_id='cd34eeee')
        cls.student7 = Student.objects.create(user=cls.user7, tucan_id='ab14eeee')
        cls.student8 = Student.objects.create(user=cls.user8, tucan_id='bc24eeee')
        cls.student9 = Student.objects.create(user=cls.user9, tucan_id='cd35eeee')

        cls.course_type = CourseType.objects.create(type='Testart')
        deadline = timezone.now()
        cls.course1 = Course.objects.create(registration_deadline=deadline, cp=5, type=cls.course_type,
                                            created_by=cls.superuser)
        cls.c1_topic1 = Topic.objects.create(title="t1", max_slots=3, min_slot_size=3, max_slot_size=5,
                                             course=cls.course1)
        cls.c1_topic2 = Topic.objects.create(title="t2", max_slots=3, min_slot_size=5, max_slot_size=5,
                                             course=cls.course1)
        cls.c1_topic3 = Topic.objects.create(title="t3", max_slots=3, min_slot_size=5, max_slot_size=5,
                                             course=cls.course1)

        cls.course2 = Course.objects.create(registration_deadline=deadline, cp=5, type=cls.course_type,
                                            created_by=cls.superuser)
        cls.c2_topic1 = Topic.objects.create(title="t1", max_slots=2, min_slot_size=1, max_slot_size=1,
                                             course=cls.course2)
        cls.c2_topic2 = Topic.objects.create(title="t2", max_slots=2, min_slot_size=1, max_slot_size=1,
                                             course=cls.course2)

        cls.group1_size3 = Group.objects.create()
        cls.group1_size3.students.add(cls.student1)
        cls.group1_size3.students.add(cls.student2)
        cls.group1_size3.students.add(cls.student3)

        cls.group2_size3 = Group.objects.create()
        cls.group2_size3.students.add(cls.student4)
        cls.group2_size3.students.add(cls.student5)
        cls.group2_size3.students.add(cls.student6)

        cls.group3_size2 = Group.objects.create()
        cls.group3_size2.students.add(cls.student7)
        cls.group3_size2.students.add(cls.student8)

        cls.group4_size1 = Group.objects.create()
        cls.group4_size1.students.add(cls.student2)

        cls.group5_size1 = Group.objects.create()
        cls.group5_size1.students.add(cls.student8)

        cls.group6_size1 = Group.objects.create()
        cls.group6_size1.students.add(cls.student9)

        # g1_ct2_t1_c4_p5 => gruppe 1 zu topic 3 in kurs 2 in collection 4 mit priority 5

        cls.app_g6_ct2_t1_c1_p1 = TopicSelection.objects.create(group=cls.group6_size1, topic=cls.c2_topic1, priority=1,
                                                                collection_number=1)
        cls.app_g6_ct2_t2_c1_p2 = TopicSelection.objects.create(group=cls.group6_size1, topic=cls.c2_topic2, priority=2,
                                                                collection_number=1)

        cls.app_g5_ct2_t1_c1_p1 = TopicSelection.objects.create(group=cls.group5_size1, topic=cls.c2_topic1, priority=1,
                                                                collection_number=1)
        cls.app_g5_ct2_t2_c2_p1 = TopicSelection.objects.create(group=cls.group5_size1, topic=cls.c2_topic2, priority=1,
                                                                collection_number=2)

        cls.app_g1_ct1_t1_c1_p1 = TopicSelection.objects.create(group=cls.group1_size3, topic=cls.c1_topic1, priority=1,
                                                                collection_number=1)

        cls.app_g2_ct1_t1_c1_p1 = TopicSelection.objects.create(group=cls.group2_size3, topic=cls.c1_topic1, priority=1,
                                                                collection_number=1)
        cls.app_g2_ct1_t1_c1_p2 = TopicSelection.objects.create(group=cls.group2_size3, topic=cls.c1_topic2, priority=2,
                                                                collection_number=1)

        cls.app_g3_ct1_t1_c1_p1 = TopicSelection.objects.create(group=cls.group3_size2, topic=cls.c1_topic1, priority=1,
                                                                collection_number=1)
        cls.app_g3_ct1_t1_c1_p2 = TopicSelection.objects.create(group=cls.group3_size2, topic=cls.c1_topic2, priority=2,
                                                                collection_number=1)

        cls.app_g4_ct1_t1_c1_p1 = TopicSelection.objects.create(group=cls.group4_size1, topic=cls.c1_topic1, priority=1,
                                                                collection_number=1)

        cls.assignment1 = Assignment.objects.create(topic=cls.c1_topic1, slot_id=1)
        cls.assignment1.accepted_applications.add(cls.app_g1_ct1_t1_c1_p1)

        cls.assignment2 = Assignment.objects.create(topic=cls.c1_topic1, slot_id=2)
        cls.assignment2.accepted_applications.add(cls.app_g2_ct1_t1_c1_p1)
        cls.assignment2.accepted_applications.add(cls.app_g3_ct1_t1_c1_p1)

        cls.assignment3 = Assignment.objects.create(topic=cls.c2_topic1, slot_id=1)
        cls.assignment3.accepted_applications.add(cls.app_g6_ct2_t1_c1_p1)

        cls.assignment4 = Assignment.objects.create(topic=cls.c2_topic1, slot_id=2)
        cls.assignment4.accepted_applications.add(cls.app_g5_ct2_t1_c1_p1)

        cls.assignment5 = Assignment.objects.create(topic=cls.c2_topic2, slot_id=1)
        cls.assignment5.accepted_applications.add(cls.app_g5_ct2_t2_c2_p1)

    def test_open_places_in_topic_count(self):
        """
        tests if the Assignment.open_places_in_topic_count property is correct
        """

        self.assertEqual(self.assignment1.open_places_in_topic_count, 7)
        self.assertEqual(self.assignment2.open_places_in_topic_count, 7)
        self.assertEqual(self.assignment3.open_places_in_topic_count, 0)
        self.assertEqual(self.assignment4.open_places_in_topic_count, 0)
        self.assertEqual(self.assignment5.open_places_in_topic_count, 1)

    def test_open_places_in_slot_count_single_group(self):
        """
        tests if the Assignment.open_places_in_slot_count property is correct if one group is assigned
        """

        self.assertEqual(self.assignment5.open_places_in_slot_count, 0)

    def test_open_places_in_slot_count_multiple_group(self):
        """
        tests if the Assignment.open_places_in_slot_count property is correct if multiple groups are assigned
        """

        self.assertEqual(self.assignment2.open_places_in_slot_count, 0)

    def test_assigned_student_to_topic_count(self):
        """
        tests if the Assignment.assigned_student_to_topic_count property is correct
        """

        self.assertEqual(self.assignment1.assigned_student_to_topic_count, 8)
        self.assertEqual(self.assignment2.assigned_student_to_topic_count, 8)
        self.assertEqual(self.assignment3.assigned_student_to_topic_count, 2)
        self.assertEqual(self.assignment4.assigned_student_to_topic_count, 2)
        self.assertEqual(self.assignment5.assigned_student_to_topic_count, 1)

    def test_assigned_student_to_slot_count_single_group(self):
        """
        tests if the Assignment.open_places_in_slot_count property is correct if one group is assigned
        """

        self.assertEqual(self.assignment1.assigned_student_to_slot_count, 3)

    def test_assigned_student_to_slot_count_multiple_group(self):
        """
        tests if the Assignment.open_places_in_slot_count property is correct if multiple groups are assigned
        """

        self.assertEqual(self.assignment2.assigned_student_to_slot_count, 5)

    def test_error_if_slot_id_not_unique(self):
        """
        tests if clean() raises a ValidationError if the slot id is not unique
        """

        assignment1_duplicate_slot_id = Assignment.objects.create(topic=self.c1_topic3, slot_id=1)
        assignment2_duplicate_slot_id = Assignment.objects.create(topic=self.c1_topic3, slot_id=1)
        with self.assertRaises(ValidationError):
            assignment2_duplicate_slot_id.clean()

    def test_error_if_group_assigned_multiple_times(self):
        """
        tests if clean() raises a ValidationError if the assigned group is already assigned to a different slot
        """

        assignment1_duplicate = Assignment.objects.create(topic=self.c1_topic3, slot_id=1)
        assignment1_duplicate.accepted_applications.add(self.app_g4_ct1_t1_c1_p1)
        with self.assertRaises(ValidationError):
            assignment1_duplicate.clean()

    def test_error_if_max_slot_size_exceeded(self):
        """
        tests if clean() raises a ValidationError if the assigned group causes the slot size to exceed the max slot size
        """

        self.assignment4.accepted_applications.add(self.app_g5_ct2_t2_c2_p1)
        with self.assertRaises(ValidationError):
            self.assignment4.clean()
