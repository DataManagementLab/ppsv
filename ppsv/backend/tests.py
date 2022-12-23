from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from course.models import Topic, Group, CourseType, Course, Student, TopicSelection
from .models import Assignment


# noinspection PyUnresolvedReferences,DuplicatedCode
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

    # noinspection PyUnusedLocal
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


# noinspection DuplicatedCode,PyUnresolvedReferences
class AssignmentViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.user4 = User.objects.create_user(username='testuser4', password='12345')
        cls.user5 = User.objects.create_user(username='testuser5', password='12345')
        cls.user6 = User.objects.create_user(username='testuser6', password='12345')

        cls.superUser1 = User.objects.create_superuser(username='testsuperuser1', password='12345')

        cls.seminar_type = CourseType.objects.create(type='Seminar')

        cls.course1 = Course.objects.create(registration_deadline=timezone.now(), cp=5, motivation_text=True,
                                            type=cls.seminar_type, title="course1", created_by=cls.superUser1)
        cls.course2 = Course.objects.create(registration_deadline=timezone.now(), cp=5, motivation_text=True,
                                            type=cls.seminar_type, title="course2", created_by=cls.superUser1)
        cls.topic1A = Topic.objects.create(course=cls.course1, title='topic1A', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic1B = Topic.objects.create(course=cls.course1, title='topic1B', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2A = Topic.objects.create(course=cls.course2, title='topic2A', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2B = Topic.objects.create(course=cls.course2, title='topic2B', max_slots=3, min_slot_size=1,
                                           max_slot_size=1)

        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee')
        cls.student4 = Student.objects.create(user=cls.user4, tucan_id='de44eeee')
        cls.student5 = Student.objects.create(user=cls.user5, tucan_id='ef55eeee')
        cls.student6 = Student.objects.create(user=cls.user6, tucan_id='fg66eeee')

        cls.group1_1_2 = Group.objects.create()
        cls.group1_1_2.students.add(cls.student1)
        cls.group1_1_2.students.add(cls.student2)

        cls.group2_3 = Group.objects.create()
        cls.group2_3.students.add(cls.student3)

        cls.group3_4 = Group.objects.create()
        cls.group3_4.students.add(cls.student4)

        cls.group4_5 = Group.objects.create()
        cls.group4_5.students.add(cls.student5)

        cls.group5_6 = Group.objects.create()
        cls.group5_6.students.add(cls.student6)

        cls.topic_selection1 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic1A, priority=1)
        cls.topic_selection1_2 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic2A, priority=1)
        cls.topic_selection2 = TopicSelection.objects.create(group=cls.group2_3, topic=cls.topic1A, priority=2)
        cls.topic_selection3 = TopicSelection.objects.create(group=cls.group3_4, topic=cls.topic1A, priority=3)
        cls.topic_selection4 = TopicSelection.objects.create(group=cls.group4_5, topic=cls.topic2A, priority=4)
        cls.topic_selection5 = TopicSelection.objects.create(group=cls.group5_6, topic=cls.topic2A, priority=4)
        cls.topic_selection1_3 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic2B, priority=1)

        cls.assignment1 = Assignment.objects.create(topic=cls.topic1A, slot_id=2)
        cls.assignment1.accepted_applications.add(cls.topic_selection1)
        cls.assignment1.accepted_applications.add(cls.topic_selection2)

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the assignment view exists at the correct location.
        """
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:assignment_page'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        response = self.client.get(reverse('backend:assignment_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:assignment_page'))

    def test_redirect_for_default_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('backend:assignment_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:assignment_page'))

    def test_view_template(self):
        """
        Tests if the assignment page view uses the correct template assignment.html.
        """
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:assignment_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend/assignment.html')

    def test_assignment_interface(self):
        """
        Tests if the assignment view displays the correct interface to make assignments.
        """
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:assignment_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Topics')
        self.assertContains(response, 'Search course/topic')
        self.assertContains(response, 'Assignments')
        self.assertContains(response, 'Applications')

    def test_select_topic(self):
        """
        Tests if the response of a select topic action is correct
        """
        data = {'action': 'selectTopic',
                'topics_of_courses': [
                    {'course': self.course1,
                     'topics': [
                         self.topic1A,
                         self.topic2A
                     ],
                     },
                    {'course': self.course2,
                     'topics': [
                         self.topic1B,
                     ],
                     }
                ],
                'topicID': 1}
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.maxDiff = None
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                "topicName": "topic1A",
                "topicMinSlotSize": 3,
                "topicMaxSlotSize": 5,
                "topicSlots": 3,
                "topicCourseName": "course1",
                "applications": [
                    {
                        "students": [
                            "ab12eeee",
                            "bc22eeee"],
                        "applicationID": 1,
                        "possibleAssignmentsForCollection": 3,
                        "collectionCount":3,
                        "preference": 1,
                        "collectionFulfilled":True,
                        "slotID": 2,
                    },
                    {
                        "students": [
                            "cd33eeee"
                        ],
                        "applicationID": 3,
                        "possibleAssignmentsForCollection": 1,
                        "collectionCount":1,
                        "preference": 2,
                        "collectionFulfilled":True,
                        "slotID": 2},
                    {
                        "students": [
                            "de44eeee"
                        ],
                        "applicationID": 4,
                        "possibleAssignmentsForCollection": 1,
                        "collectionCount":1,
                        "preference": 3,
                        "collectionFulfilled":False,
                        "slotID": -1
                    }
                ]
            }
        )

    def test_new_Assignment(self):
        """
        Tests if the response of a new assignment action is correct
        """

        if Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.get(topic=self.topic2A, slot_id=1).delete()

        data = {'action': 'newAssignment',
                'topic_id': 3,
                'slotID': 1,
                'applicationID': 5
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Saved to Database"
            }
        )

        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection4))

    def test_new_Assignment_does_not_exists(self):
        """
        Tests if the response of a new assignment action is correct when the new Assignment already exists
        """

        data = {'action': 'newAssignment',
                'topic_id': 3,
                'slotID': 1,
                'applicationID': 69
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "This assignment exists already"
            }
        )

    def test_new_Assignment_not_enough_space_in_slot(self):
        """
        Tests if the response of a new assignment action is correct when the new Assignment already exists
        """

        data = {'action': 'newAssignment',
                'topic_id': self.topic2B.id,
                'slotID': 1,
                'applicationID': self.topic_selection1_3.id
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "No Space in Slot"
            }
        )

    def test_remove_Assignment(self):
        """
        Tests if the response of a remove assignment topic action is correct
        """

        if not Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.create(topic=self.topic2A, slot_id=1)

        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection4)

        data = {'action': 'removeAssignment',
                'slotID': 1,
                'applicationID': 5
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Assignment deleted"
            }
        )

        self.assertFalse(Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists())

    def test_remove_Assignment_multiple_groups(self):
        """
        Tests if the response of a remove assignment topic action is correct when multiple groups are assigned to a
        topic
        """

        if not Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.create(topic=self.topic2A, slot_id=1)

        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection4)
        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection5)

        data = {'action': 'removeAssignment',
                'slotID': 1,
                'applicationID': 5
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Assignment deleted"
            }
        )

        self.assertFalse(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection4))
        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection5))

    def test_change_Assignment(self):
        """
        Tests if the response of a remove assignment topic action is correct when multiple groups are assigned to a
        topic
        """

        if not Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.create(topic=self.topic2A, slot_id=1)

        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection4)
        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection5)

        data = {'action': 'changeAssignment',
                'oldSlotID': 1,
                'newSlotID': 3,
                'applicationID': 5
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Saved to Database"
            }
        )

        self.assertFalse(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection4))
        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection5))

        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=3).accepted_applications.contains(self.topic_selection4))
        self.assertFalse(
            Assignment.objects.get(topic=self.topic2A, slot_id=3).accepted_applications.contains(self.topic_selection5))

    def test_filter_exists(self):
        """
        tests if the filter options are shown correctly
        """

        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:assignment_page'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'CP:')
        self.assertContains(response, 'Choose CP')

        self.assertContains(response, 'Course Type:')
        self.assertContains(response, 'Choose Course Typ')

        self.assertContains(response, 'Faculty:')
        self.assertContains(response, 'Choose Faculty')

