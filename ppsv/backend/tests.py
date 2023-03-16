from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from course.models import Topic, Group, CourseType, Course, Student, TopicSelection, Term
from .automatic_assignment import main as automatic_assigment
from .models import Assignment, AcceptedApplications, TermFinalization
from .pages import admin_page, home_page


# noinspection PyUnresolvedReferences,DuplicatedCode,DjangoOrm
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
        cls.deadline = timezone.now()

        cls.term = Term.objects.create(name="WiSe22/23", active_term=True, registration_start=cls.deadline,
                                       registration_deadline=cls.deadline)
        cls.term2_finalized = Term.objects.create(name="SoSe22", active_term=False, registration_start=cls.deadline,
                                                  registration_deadline=cls.deadline)
        TermFinalization.objects.create(term=cls.term2_finalized, finalized=True)

        cls.course1 = Course.objects.create(registration_start=cls.deadline,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            type=cls.course_type,
                                            created_by=cls.superuser,
                                            term=cls.term)
        cls.c1_topic1 = Topic.objects.create(title="t1", max_slots=3, min_slot_size=3, max_slot_size=5,
                                             course=cls.course1)
        cls.c1_topic2 = Topic.objects.create(title="t2", max_slots=3, min_slot_size=5, max_slot_size=5,
                                             course=cls.course1)
        cls.c1_topic3 = Topic.objects.create(title="t3", max_slots=3, min_slot_size=5, max_slot_size=5,
                                             course=cls.course1)

        cls.course2 = Course.objects.create(registration_start=cls.deadline,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            type=cls.course_type,
                                            created_by=cls.superuser,
                                            term=cls.term)
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

        cls.assignment6_finalized1 = Assignment.objects.create(topic=cls.c1_topic1, slot_id=3, finalized_slot=1)
        cls.assignment7_finalized2 = Assignment.objects.create(topic=cls.c1_topic1, slot_id=4, finalized_slot=2)
        cls.assignment8_finalized3 = Assignment.objects.create(topic=cls.c1_topic1, slot_id=5, finalized_slot=3)

        accepted_application1 = AcceptedApplications.objects.get(topic_selection=cls.app_g1_ct1_t1_c1_p1,
                                                                 assignment=cls.assignment1)
        accepted_application1.finalized_assignment = True
        accepted_application1.save()

        accepted_application2 = AcceptedApplications.objects.get(topic_selection=cls.app_g3_ct1_t1_c1_p1,
                                                                 assignment=cls.assignment2)
        accepted_application2.finalized_assignment = True
        accepted_application2.save()

    def test_is_finalized(self):
        """
        tests if the TermFinalisation.is_finalized property is correct
        """

        self.assertFalse(TermFinalization.is_finalized(self.term))
        self.assertTrue(TermFinalization.is_finalized(self.term2_finalized))

    def test_assigned_student_to_topic_count(self):
        """
        tests if Assignment.assigned_student_to_topic_count property is correct
        """

        self.assertEqual(Assignment.assigned_student_to_topic_count(self.c1_topic1), 8)
        self.assertEqual(Assignment.assigned_student_to_topic_count(self.c1_topic2), 0)
        self.assertEqual(Assignment.assigned_student_to_topic_count(self.c1_topic3), 0)
        self.assertEqual(Assignment.assigned_student_to_topic_count(self.c2_topic1), 2)
        self.assertEqual(Assignment.assigned_student_to_topic_count(self.c2_topic2), 1)

    def test_locked(self):
        """
        tests if the Assignment.locked property is correct
        """

        self.assertFalse(self.assignment1.locked)
        self.assertFalse(self.assignment2.locked)
        self.assertFalse(self.assignment3.locked)
        self.assertFalse(self.assignment4.locked)
        self.assertFalse(self.assignment5.locked)

        self.assertTrue(self.assignment6_finalized1)
        self.assertTrue(self.assignment7_finalized2)
        self.assertTrue(self.assignment8_finalized3)

    def test_has_open_places(self):
        """"
        tests if the Assignment.has_open_places property is correct
        """

        self.assertEqual(Assignment.has_open_places(self.c1_topic1), 7)
        self.assertEqual(Assignment.has_open_places(self.c1_topic2), 15)
        self.assertEqual(Assignment.has_open_places(self.c1_topic3), 15)
        self.assertEqual(Assignment.has_open_places(self.c2_topic1), 0)
        self.assertEqual(Assignment.has_open_places(self.c2_topic2), 1)

    def test_max_assigned_student_to_slot(self):
        """
        test if the Assignment.max_assigned_student_to_slot property is correct
        """

        self.assertEqual(self.assignment1.max_assigned_student_to_slot, 5)
        self.assertEqual(self.assignment2.max_assigned_student_to_slot, 5)
        self.assertEqual(self.assignment3.max_assigned_student_to_slot, 1)
        self.assertEqual(self.assignment4.max_assigned_student_to_slot, 1)
        self.assertEqual(self.assignment5.max_assigned_student_to_slot, 1)
        self.assertEqual(self.assignment6_finalized1.max_assigned_student_to_slot, 5)
        self.assertEqual(self.assignment7_finalized2.max_assigned_student_to_slot, 5)
        self.assertEqual(self.assignment8_finalized3.max_assigned_student_to_slot, 5)

    def test_any_application_locked(self):
        """
        test if the Assignment.any_application_locked property is correct
        """
        self.assertEqual(self.assignment1.any_application_locked, True)
        self.assertEqual(self.assignment2.any_application_locked, True)
        self.assertEqual(self.assignment3.any_application_locked, False)
        self.assertEqual(self.assignment4.any_application_locked, False)
        self.assertEqual(self.assignment5.any_application_locked, False)

    def test_str(self):
        """
        tests if the __str__ method is correct
        """

        self.assertEqual(self.assignment1.__str__(), "Slot 1 of topic \"t1\" [3/5]")
        self.assertEqual(self.assignment2.__str__(), "Slot 2 of topic \"t1\" [5/5]")
        self.assertEqual(self.assignment3.__str__(), "Slot 1 of topic \"t1\"")
        self.assertEqual(self.assignment4.__str__(), "Slot 2 of topic \"t1\"")
        self.assertEqual(self.assignment5.__str__(), "Slot 1 of topic \"t2\"")

    def test_get_dict_key(self):
        """
        tests if the get_dict_key property is correct
        """

        expected = {
            (self.group6_size1, 1): self.app_g6_ct2_t1_c1_p1,
            (self.group5_size1, 1): self.app_g5_ct2_t1_c1_p1,
            (self.group5_size1, 2): self.app_g5_ct2_t2_c2_p1,
            (self.group1_size3, 1): self.app_g1_ct1_t1_c1_p1,
            (self.group2_size3, 1): self.app_g2_ct1_t1_c1_p1,
            (self.group3_size2, 1): self.app_g3_ct1_t1_c1_p1
        }

        self.assertDictEqual(AcceptedApplications.get_collection_dict(), expected)

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

        assignment1_duplicate = Assignment.objects.create(topic=self.c1_topic1, slot_id=1)
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


# noinspection DuplicatedCode,PyUnresolvedReferences,DjangoOrm
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

        cls.deadline = timezone.now()
        cls.deadline += timedelta(days=1)
        cls.start = timezone.now()
        cls.start -= timedelta(days=1)

        cls.term = Term.objects.create(name="WiSe22/23", active_term=True, registration_start=cls.start,
                                       registration_deadline=cls.deadline)
        cls.term_finalized = Term.objects.create(name="SoSe22", active_term=False, registration_start=cls.start,
                                                 registration_deadline=cls.deadline)
        TermFinalization.objects.create(term=cls.term_finalized, finalized=True)

        cls.course1 = Course.objects.create(registration_start=cls.start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course1",
                                            faculty="FB20",
                                            created_by=cls.superUser1,
                                            term=cls.term)
        cls.course2 = Course.objects.create(registration_start=cls.start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            faculty="FB18",
                                            title="course2",
                                            created_by=cls.superUser1,
                                            term=cls.term)
        cls.course_finalized = Course.objects.create(registration_start=cls.start,
                                                     registration_deadline=cls.deadline,
                                                     cp=5,
                                                     motivation_text=True,
                                                     type=cls.seminar_type,
                                                     title="course_finalized",
                                                     faculty="FB20",
                                                     created_by=cls.superUser1,
                                                     term=cls.term_finalized)

        cls.topic1A = Topic.objects.create(course=cls.course1, title='topic1A', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic1B = Topic.objects.create(course=cls.course1, title='topic1B', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2A = Topic.objects.create(course=cls.course2, title='topic2A', max_slots=3, min_slot_size=1,
                                           max_slot_size=2)
        cls.topic2B = Topic.objects.create(course=cls.course2, title='topic2B', max_slots=3, min_slot_size=1,
                                           max_slot_size=1)
        cls.topic3A = Topic.objects.create(course=cls.course_finalized, title='topic3A', max_slots=3, min_slot_size=1,
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
        cls.topic_selection2_2 = TopicSelection.objects.create(group=cls.group2_3, topic=cls.topic2B, priority=2,
                                                               collection_number=2)
        cls.topic_selection2_3 = TopicSelection.objects.create(group=cls.group2_3, topic=cls.topic2B, priority=2,
                                                               collection_number=3)
        cls.topic_selection3 = TopicSelection.objects.create(group=cls.group3_4, topic=cls.topic1A, priority=3)
        cls.topic_selection4 = TopicSelection.objects.create(group=cls.group4_5, topic=cls.topic2A, priority=4)
        cls.topic_selection5 = TopicSelection.objects.create(group=cls.group5_6, topic=cls.topic2A, priority=4)
        cls.topic_selection1_3 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic2B, priority=1,
                                                               collection_number=2)
        cls.topic_selection1_4 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic2A, priority=1,
                                                               collection_number=3)
        cls.topic_selection2_1 = TopicSelection.objects.create(group=cls.group2_3, topic=cls.topic2A, priority=1,
                                                               collection_number=2)
        cls.assignment1 = Assignment.objects.create(topic=cls.topic1A, slot_id=2)
        cls.assignment1.accepted_applications.add(cls.topic_selection1)
        cls.assignment1.accepted_applications.add(cls.topic_selection2)
        cls.assignment2 = Assignment.objects.create(topic=cls.topic2B, slot_id=2, finalized_slot=1)
        cls.assignment2.accepted_applications.add(cls.topic_selection1_3)
        cls.assignment3 = Assignment.objects.create(topic=cls.topic2B, slot_id=3)
        cls.acceptedApplication3 = AcceptedApplications.objects.create(assignment=cls.assignment3,
                                                                       topic_selection=cls.topic_selection2_2,
                                                                       finalized_assignment=True)
        cls.assignment4 = Assignment.objects.create(topic=cls.topic2B, slot_id=4)
        cls.acceptedApplication4 = AcceptedApplications.objects.create(assignment=cls.assignment4,
                                                                       topic_selection=cls.topic_selection2_3,
                                                                       finalized_assignment=True)

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
        self.assertContains(response, 'Filter')
        self.assertContains(response, 'Statistics')
        self.assertContains(response, 'Home Page')
        self.assertContains(response, 'Django Admin')
        self.assertContains(response, 'Admin Controls')
        self.assertContains(response, 'Group Details')
        self.assertContains(response, 'Override Slot')
        self.assertContains(response, 'Override Application')
        self.assertContains(response, 'Open first open Application of group')
        self.assertContains(response, 'Groups by currently assigned priority')
        self.assertContains(response, 'Broken Slots')

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
                "topicSlotsFinalized": [0, 0, 0],
                "topicSlots": 3,
                "topicCourseName": "course1",
                "applications": [
                    {
                        "students": [
                            "ab12eeee",
                            "bc22eeee"],
                        "applicationID": self.topic_selection1.id,
                        "possibleAssignmentsForCollection": 2,
                        "collectionCount": 2,
                        "preference": 1,
                        "collectionFulfilled": True,
                        "slotID": 2,
                        "groupID": 1,
                        "collectionID": 1,
                        "finalizedAssignment": False,
                    },
                    {
                        "students": [
                            "cd33eeee"
                        ],
                        "applicationID": self.topic_selection2.id,
                        "possibleAssignmentsForCollection": 1,
                        "collectionCount": 1,
                        "preference": 2,
                        "collectionFulfilled": True,
                        "slotID": 2,
                        "groupID": 2,
                        "collectionID": 1,
                        "finalizedAssignment": False,
                    },
                    {
                        "students": [
                            "de44eeee"
                        ],
                        "applicationID": self.topic_selection3.id,
                        "possibleAssignmentsForCollection": 1,
                        "collectionCount": 1,
                        "preference": 3,
                        "collectionFulfilled": False,
                        "slotID": -1,
                        "groupID": 3,
                        "collectionID": 1,
                        "finalizedAssignment": False,
                    }
                ]
            }
        )

    def test_new_assignment_satisfied(self):
        """
        Tests if the response of a new assignment action is correct when the group is already assigned to a topic
        """

        if not Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            assignment = Assignment.objects.create(topic=self.topic2A, slot_id=1)
            AcceptedApplications.objects.create(topic_selection=self.topic_selection1_2, assignment=assignment)

        data = {'action': 'newAssignment',
                'topic_id': self.topic1A.id,
                'slotID': 1,
                'applicationID': self.topic_selection1.id
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "The collection of this group is already satisfied"
            }
        )

        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(
                self.topic_selection1_2))

        self.assertFalse(Assignment.objects.filter(topic=self.topic1A, slot_id=1).exists())

    def test_new_Assignment(self):
        """
        Tests if the response of a new assignment action is correct
        """

        if Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.get(topic=self.topic2A, slot_id=1).delete()

        data = {'action': 'newAssignment',
                'topic_id': self.topic2A.id,
                'slotID': 1,
                'applicationID': self.topic_selection4.id
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

        data = {'action': 'newAssignment',
                'topic_id': self.topic2A.id,
                'slotID': 1,
                'applicationID': self.topic_selection1_4.id
                }

        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "No Space in Slot"
            }
        )

        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection4))
        self.assertFalse(Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(
            self.topic_selection1_4))

        data = {'action': 'newAssignment',
                'topic_id': self.topic2A.id,
                'slotID': 1,
                'applicationID': self.topic_selection5.id
                }

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
        self.assertTrue(
            Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.contains(self.topic_selection5))

    def test_new_Assignment_does_not_exists(self):
        """
        Tests if the response of a new assignment that does not exist in the database
        """

        data = {'action': 'newAssignment',
                'topic_id': 3,
                'slotID': 1,
                'applicationID': 69
                }
        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 500)

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
                'text': "This is an illegal application for this slot: it does not fit into it!"
            }
        )

    def test_select_application(self):
        """
        Tests if the response of an application selection action is correct
        """

        data = {
            'action': 'selectApplication',
            'applicationID': self.topic_selection1.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"selectedGroup": 1, "selectedCollection": 1, "members": ["ab12eeee", "bc22eeee"], "assigned": 1,
             "collection": [{"id": 1, "name": "topic1A", "priority": 1, "freeSlots": 3},
                            {"id": 3, "name": "topic2A", "priority": 1, "freeSlots": 3}]}
        )

    def test_handle_change_finalized_value_slot(self):
        """
        Tests if the response of a change finalized value slot action is correct
        """

        slotID = 5
        topic = Topic.objects.create(course=self.course2, min_slot_size=0, max_slot_size=2, max_slots=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=0)

        # lock
        data = {
            'action': 'changeFinalizedValueSlot',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'newFinalized': 1
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        assignment = Assignment.objects.get(id=assignment.id)

        self.assertEqual(1, assignment.finalized_slot)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Slot has been locked",
            }
        )

        # unlock
        data = {
            'action': 'changeFinalizedValueSlot',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'newFinalized': 0
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        assignment = Assignment.objects.get(id=assignment.id)

        self.assertEqual(0, assignment.finalized_slot)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Slot has been unlocked",
            }
        )

    def test_handle_change_finalized_value_slot_not_full(self):
        """
        Tests if the response of a change finalized value slot action is correct when the slot does not contain the minimum amount of students
        """

        slotID = 5
        topic = Topic.objects.create(course=self.course2, min_slot_size=1, max_slot_size=2, max_slots=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=0)

        # lock
        data = {
            'action': 'changeFinalizedValueSlot',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'newFinalized': 1
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        assignment = Assignment.objects.get(id=assignment.id)

        self.assertEqual(0, assignment.finalized_slot)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "Only slots with the minimum amount of needed applications can be locked",
            }
        )

    def test_handle_change_finalized_value_slot_finalization_too_high(self):
        """
        Tests if the response of a change finalized value slot action is correct when the lock state is too high
        """

        slotID = 5
        topic = Topic.objects.create(course=self.course2, min_slot_size=1, max_slot_size=2, max_slots=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=2)

        # lock
        data = {
            'action': 'changeFinalizedValueSlot',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'newFinalized': 1
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        assignment = Assignment.objects.get(id=assignment.id)

        self.assertEqual(2, assignment.finalized_slot)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "Slot can't be unlocked",
            }
        )

    def test_handle_get_statistic_data(self):
        """
        Tests if the response of a get statistic data action is correct
        """

        data = {
            'action': 'getStatisticData',
            'minCP': 0,
            'maxCP': 6,
            'courseTypes[]': [
                self.seminar_type.id
            ],
            "faculties[]": [
                "FB20"
            ]
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"groups": [1, 1, 0, 0, 0, 0, 1], "students": [2, 1, 0, 0, 0, 0, 1], "score": "80.38 %", "brokenSlots": 1,
             "notAssignedGroups": 1}
        )

    def test_handle_get_topics_filtered(self):
        """
        Tests if the response of a get topics filtered action is correct
        """

        data = {
            'action': 'getTopicsFiltered',
            'minCP': 0,
            'maxCP': 6,
            'courseTypes[]': [
                self.seminar_type.id
            ],
            "faculties[]": [
                "FB20"
            ],
            'special': 1
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(str(response.content, encoding='utf8'), {"filteredTopics": [1, 2]})

        data = {
            'action': 'getTopicsFiltered',
            'minCP': 0,
            'maxCP': 6,
            'courseTypes[]': [
                self.seminar_type.id
            ],
            "faculties[]": [
                "FB20"
            ],
            'special': 2
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(str(response.content, encoding='utf8'), {"filteredTopics": [1]})

    def test_handle_change_finalized_value_slot_term_finalized(self):
        """
        Tests if the response of a change finalized value slot action is correct when the term is finalized
        """

        self.term_finalized.active_term = True
        self.term_finalized.save()

        self.term.active_term = False
        self.term.save()

        slotID = 5
        topic = Topic.objects.create(course=self.course_finalized, min_slot_size=0, max_slot_size=2, max_slots=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=1)

        # lock
        data = {
            'action': 'changeFinalizedValueSlot',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'newFinalized': 0
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        assignment = Assignment.objects.get(id=assignment.id)

        self.assertEqual(3, assignment.finalized_slot)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "Slot can't be unlocked",
            }
        )

        self.term_finalized.active_term = False
        self.term_finalized.save()

        self.term.active_term = True
        self.term.save()

    def test_handle_get_bulk_applications_update(self):
        """
        Tests if the response of a get bulk application update action is correct
        """

        data = {
            'action': 'getBulkApplicationsUpdate',
            'applicationIDs[]': [
                self.topic_selection1.id,
                self.topic_selection2.id,
                self.topic_selection3.id,
            ]
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"1": {"possibleAssignments": 2, "collectionFulfilled": True},
             "3": {"possibleAssignments": 1, "collectionFulfilled": True},
             "6": {"possibleAssignments": 1, "collectionFulfilled": False}}
        )

    def test_handle_clear_slot(self):
        """
        Tests if the response of a clear slot action is correct
        """

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)

        data = {
            "action": "clearSlot",
            "assignmentID": assignment.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(Assignment.objects.filter(id=assignment.id).exists())

    def test_handle_load_group_data(self):
        """
        Tests if the response of a load group data action is correct
        """

        data = {
            "action": "loadGroupData",
            "groupID": self.group1_1_2.id,
            "collectionID": self.topic_selection1.collection_number
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             '{"selectedGroup": "1", "selectedCollection": "1", "members": ["ab12eeee", "bc22eeee"], '
                             '"assigned": 1, "collection": [{"id": 1, "name": "topic1A", "priority": 1, "freeSlots": '
                             '3}, {"id": 3, "name": "topic2A", "priority": 1, "freeSlots": 3}]}')

    def test_handle_groups_by_prio(self):
        """
        Tests if the response of a groups by priority action is correct
        """

        data = {
            'action': 'groupsByPrio'
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"0": [[1, 3], [3, 1], [4, 1], [5, 1]], "1": [[1, 1], [1, 2]], "2": [[2, 1], [2, 2], [2, 3]], "3": [],
             "4": [], "5": [], "6": []}
        )

    def test_handle_get_broken_slots(self):
        """
        Tests if the response of a get broken slot action is correct
        """

        data = {
            'action': 'getBrokenSlots'
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"brokenSlots": [[], [[4, 2, "Slot 2 of topic \"topic2B\"",
                                   "['This assignment exceeds the maximum slot size of the assigned topic']"]]]}
        )

    def test_invalid_action(self):
        """
        Tests if the response of an invalid action is correct
        """

        data = {
            'action': 'invalidAction'
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 501)

        self.assertEqual(response.content,
                         b"invalid request action: invalidAction. Please report this and the actions you took to get "
                         b"this message to an administrator!")

    def test_no_action(self):
        """
        Tests if the response is correct when no action is given
        """

        data = {
            'Hello': 'World!'
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 501)

        self.assertEqual(response.content, b"POST request didn't specify an action. Please report this and the actions "
                                           b"you took to get this message to the administrator!")

    def test_handle_change_finalized_value_application(self):
        """
        Tests if the response of a change finalized value application action is correct
        """

        slotID = 5
        topic = Topic.objects.create(course=self.course2, min_slot_size=0, max_slot_size=2, max_slots=1)
        topic_selection = TopicSelection.objects.create(group=self.group2_3, topic=topic, priority=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=0)
        accepted_application = AcceptedApplications.objects.create(assignment=assignment,
                                                                   topic_selection=topic_selection)

        # lock
        data = {
            'action': 'changeFinalizedValueApplication',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'applicationID': topic_selection.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        accepted_application = AcceptedApplications.objects.get(id=accepted_application.id)

        self.assertTrue(accepted_application.finalized_assignment)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Assignment has been locked",
            }
        )

        # unlock
        data = {
            'action': 'changeFinalizedValueApplication',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'applicationID': topic_selection.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        accepted_application = AcceptedApplications.objects.get(id=accepted_application.id)

        self.assertFalse(accepted_application.finalized_assignment)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': True,
                'text': "Assignment has been unlocked",
            }
        )

    def test_handle_change_finalized_value_Application_finalization_too_high(self):
        """
        Tests if the response of a change finalized value application action is correct when the lock state is too high
        """

        slotID = 5
        topic = Topic.objects.create(course=self.course2, min_slot_size=0, max_slot_size=2, max_slots=1)
        topic_selection = TopicSelection.objects.create(group=self.group2_3, topic=topic, priority=1)
        assignment = Assignment.objects.create(topic=topic, slot_id=slotID, finalized_slot=2)
        accepted_application = AcceptedApplications.objects.create(assignment=assignment,
                                                                   topic_selection=topic_selection)

        data = {
            'action': 'changeFinalizedValueApplication',
            'slotID': slotID,
            'slotTopicID': topic.id,
            'applicationID': topic_selection.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        accepted_application = AcceptedApplications.objects.get(id=accepted_application.id)

        self.assertFalse(accepted_application.finalized_assignment)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "Application can't be (un)locked",
            }
        )

    def test_remove_slot_locked(self):
        """
        Tests if the response of a remove assignment topic action is correct when the slot is locked
        """

        data = {
            'action': 'removeAssignment',
            'slotID': 2,
            'applicationID': self.topic_selection1_3.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "This slot is locked and can not be changed"
            }
        )

        self.assertTrue(Assignment.objects.filter(topic=self.topic2B, slot_id=2).exists())
        self.assertTrue(Assignment.objects.get(topic=self.topic2B, slot_id=2).accepted_applications.contains(
            self.topic_selection1_3))

    def test_remove_assignment_locked(self):
        """
        Tests if the response of a remove assignment topic action is correct when the assignment is locked
        """

        data = {'action': 'removeAssignment',
                'slotID': 3,
                'applicationID': self.topic_selection2_2.id
                }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:assignment_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'requestStatus': False,
                'text': "This assignment is locked and cannot be changed"
            }
        )

        self.assertTrue(Assignment.objects.filter(topic=self.topic2B, slot_id=3).exists())
        self.assertTrue(Assignment.objects.get(topic=self.topic2B, slot_id=3).accepted_applications.contains(
            self.topic_selection2_2))

    def test_remove_Assignment(self):
        """
        Tests if the response of a remove assignment topic action is correct
        """

        if not Assignment.objects.filter(topic=self.topic2A, slot_id=1).exists():
            Assignment.objects.create(topic=self.topic2A, slot_id=1)

        Assignment.objects.get(topic=self.topic2A, slot_id=1).accepted_applications.add(self.topic_selection4)

        data = {'action': 'removeAssignment',
                'slotID': 1,
                'applicationID': self.topic_selection4.id
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
                'applicationID': self.topic_selection4.id
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
                'applicationID': self.topic_selection4.id
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


# noinspection DuplicatedCode,PyUnresolvedReferences,DjangoOrm
class AdminPageTest(TestCase):

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
        cls.praktikum_type = CourseType.objects.create(type='Praktikum')

        cls.deadline = timezone.now()
        cls.deadline += timedelta(days=1)
        start = timezone.now()
        start -= timedelta(days=1)

        cls.term = Term.objects.create(name="WiSe22/23", active_term=True, registration_start=start,
                                       registration_deadline=cls.deadline)

        cls.course1 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course1",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course2 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course2",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB18")
        cls.course3 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=8,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course3",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course4 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=3,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course4",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.topic1A = Topic.objects.create(course=cls.course1, title='topic1A', max_slots=10, min_slot_size=3,
                                           max_slot_size=4)
        cls.topic1B = Topic.objects.create(course=cls.course2, title='topic1B', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2A = Topic.objects.create(course=cls.course3, title='topic2A', max_slots=3, min_slot_size=1,
                                           max_slot_size=5)
        cls.topic2B = Topic.objects.create(course=cls.course4, title='topic2B', max_slots=3, min_slot_size=1,
                                           max_slot_size=2)

        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee', email="test1@test.com")
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee', email="test2@test.com")
        cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee', email="test3@test.com")
        cls.student4 = Student.objects.create(user=cls.user4, tucan_id='de44eeee', email="test4@test.com")
        cls.student5 = Student.objects.create(user=cls.user5, tucan_id='ef55eeee', email="test5@test.com")
        cls.student6 = Student.objects.create(user=cls.user6, tucan_id='fg66eeee', email="test6@test.com")

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
        cls.topic_selection1_3 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic2B, priority=1)
        cls.topic_selection1_4 = TopicSelection.objects.create(group=cls.group1_1_2, topic=cls.topic1A, priority=1,
                                                               collection_number=2)
        cls.topic_selection2 = TopicSelection.objects.create(group=cls.group2_3, topic=cls.topic1A, priority=2)
        cls.topic_selection3 = TopicSelection.objects.create(group=cls.group3_4, topic=cls.topic1A, priority=3)
        cls.topic_selection4 = TopicSelection.objects.create(group=cls.group4_5, topic=cls.topic2A, priority=4)
        cls.topic_selection5 = TopicSelection.objects.create(group=cls.group5_6, topic=cls.topic1A, priority=4)

        cls.assignment1 = Assignment.objects.create(topic=cls.topic1A, slot_id=2)
        cls.assignment1.accepted_applications.add(cls.topic_selection1)
        cls.assignment1.accepted_applications.add(cls.topic_selection2)

        cls.assignment2 = Assignment.objects.create(topic=cls.topic2B, slot_id=1, finalized_slot=1)
        cls.assignment2.accepted_applications.add(cls.topic_selection1_3)

        cls.assignment3 = Assignment.objects.create(topic=cls.topic2A, slot_id=1, finalized_slot=2)
        cls.assignment3.accepted_applications.add(cls.topic_selection4)

    def test_admin_page_template(self):
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:admin_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend/admin.html')

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the assignment view exists at the correct location.
        """
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:admin_page'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        response = self.client.get(reverse('backend:admin_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:admin_page'))

    def test_redirect_for_default_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('backend:admin_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:admin_page'))

    def test_handle_finalize(self):
        """
        tests if the response of a handle_finalize request is correct
        """

        data = {
            "action": "finalize",
            "finalize": "true"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "success": "true"
        })

        self.assertTrue(TermFinalization.objects.get(term=self.term).finalized)
        self.assertEqual(Assignment.objects.get(id=self.assignment1.id).finalized_slot, 2)
        self.assertEqual(Assignment.objects.get(id=self.assignment2.id).finalized_slot, 3)
        self.assertEqual(Assignment.objects.get(id=self.assignment3.id).finalized_slot, 2)

        data = {
            "action": "finalize",
            "finalize": "false"
        }

        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "success": "true"
        })

        self.assertFalse(TermFinalization.objects.get(term=self.term).finalized)
        self.assertEqual(Assignment.objects.get(id=self.assignment1.id).finalized_slot, 0)
        self.assertEqual(Assignment.objects.get(id=self.assignment2.id).finalized_slot, 1)
        self.assertEqual(Assignment.objects.get(id=self.assignment3.id).finalized_slot, 0)

        self.assignment3 = Assignment.objects.get(id=self.assignment3.id)
        self.assignment3.finalized_slot = 2
        self.assignment3.save()

    def test_handle_finalize_mails_send(self):
        """
        tests if the response of a handle_finalize request is correct when the mails for the term were already send
        """

        data = {
            "action": "finalize",
            "finalize": "false"
        }

        TermFinalization.objects.create(term=self.term, finalized=True, mails_send=True)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 500)

        self.assertEqual(response.content, b"Emails got already send for this Term. Term is not changeable anymore")

        self.assertTrue(TermFinalization.objects.get(term=self.term).finalized)
        self.assertEqual(Assignment.objects.get(id=self.assignment1.id).finalized_slot, 0)
        self.assertEqual(Assignment.objects.get(id=self.assignment2.id).finalized_slot, 1)
        self.assertEqual(Assignment.objects.get(id=self.assignment3.id).finalized_slot, 2)

        TermFinalization.objects.get(term=self.term).delete()

    def test_handle_finalize_less_than_min_slot_size(self):
        """
        tests if the response of a handle_finalize request is correct when to few students are assigned to a slot
        """

        data = {
            "action": "finalize",
            "finalize": "true"
        }

        TermFinalization.objects.create(term=self.term, finalized=False, mails_send=False)

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "success": "false"
        })

        self.assertFalse(TermFinalization.objects.get(term=self.term).finalized)
        self.assertEqual(Assignment.objects.get(id=self.assignment1.id).finalized_slot, 0)
        self.assertEqual(Assignment.objects.get(id=self.assignment2.id).finalized_slot, 1)
        self.assertEqual(Assignment.objects.get(id=self.assignment3.id).finalized_slot, 2)

        Assignment.objects.get(id=assignment.id).delete()

    def test_handle_finalize_more_than_max_slot_size(self):
        """
        tests if the response of a handle_finalize request is correct when to many students are assigned to a slot
        """

        data = {
            "action": "finalize",
            "finalize": "true"
        }

        TermFinalization.objects.create(term=self.term, finalized=False, mails_send=False)

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)
        assignment.accepted_applications.add(self.topic_selection3)
        assignment.accepted_applications.add(self.topic_selection1_4)
        assignment.accepted_applications.add(self.topic_selection5)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "success": "false"
        })

        self.assertFalse(TermFinalization.objects.get(term=self.term).finalized)
        self.assertEqual(Assignment.objects.get(id=self.assignment1.id).finalized_slot, 0)
        self.assertEqual(Assignment.objects.get(id=self.assignment2.id).finalized_slot, 1)
        self.assertEqual(Assignment.objects.get(id=self.assignment3.id).finalized_slot, 2)

        Assignment.objects.get(id=assignment.id).delete()

    def test_handle_start_automatic_assignment(self):
        """
        tests if the response of a handle_start_automatic_assignment request is correct
        """

        data = {
            "action": "startAutomaticAssignment",
            "override": "false"
        }

        automatic_assigment.running = False
        automatic_assigment.iterations = 1

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 205)

    def test_handle_remove_broken_slots(self):
        """
        tests if the response of a handle_remove_broken_slots request is correct
        """

        data = {
            "action": "removeBrokenSlots"
        }

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 205)

        self.assertTrue(Assignment.objects.filter(id=self.assignment1.id).exists())
        self.assertTrue(Assignment.objects.filter(id=self.assignment2.id).exists())
        self.assertTrue(Assignment.objects.filter(id=self.assignment3.id).exists())
        self.assertFalse(Assignment.objects.filter(id=assignment.id).exists())

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)
        assignment.accepted_applications.add(self.topic_selection3)
        assignment.accepted_applications.add(self.topic_selection1_4)
        assignment.accepted_applications.add(self.topic_selection5)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 205)

        self.assertTrue(Assignment.objects.filter(id=self.assignment1.id).exists())
        self.assertTrue(Assignment.objects.filter(id=self.assignment2.id).exists())
        self.assertTrue(Assignment.objects.filter(id=self.assignment3.id).exists())
        self.assertFalse(Assignment.objects.filter(id=assignment.id).exists())

    def test_send_email(self):
        """
        tests if the response of a send_email request is correct
        """

        term_finalization = TermFinalization.objects.create(term=self.term, finalized=True, mails_send=False)
        accepted_application1 = AcceptedApplications.objects.create(assignment=self.assignment1,
                                                                    topic_selection=self.topic_selection1)
        accepted_application2 = AcceptedApplications.objects.create(assignment=self.assignment1,
                                                                    topic_selection=self.topic_selection2)
        accepted_application3 = AcceptedApplications.objects.create(assignment=self.assignment2,
                                                                    topic_selection=self.topic_selection1_3)
        accepted_application4 = AcceptedApplications.objects.create(assignment=self.assignment3,
                                                                    topic_selection=self.topic_selection4)

        data = {
            "action": "sendEmails"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 6)

        expected_subject = 'Information zur Praktikums- und Seminarplatzvergabe ' + self.term.name + ' / Information for Internship & Seminar Allocation ' + self.term.name
        expected_from_email = "PPSV <info@ppsv.tu-darmstadt.de>"

        for i in range(0, 5):
            self.assertEqual(mail.outbox[i].subject, expected_subject)
            self.assertEqual(mail.outbox[i].from_email, expected_from_email)

        for student in Student.objects.all():
            contains = False
            for email in mail.outbox:
                if email.to == [student.email]:
                    contains = True

                    # test body
                    query = AcceptedApplications.objects.filter(topic_selection__group__students__in=[student])
                    if query.exists():
                        self.assertIn("You (or your Groups) were assigned to the following Topics", email.body)
                        for accepted_application in query:
                            self.assertIn(accepted_application.assignment.topic.title, email.body)
                            self.assertIn(accepted_application.assignment.topic.course.title, email.body)
                    else:
                        self.assertIn("Unfortunately, you (or your Groups) did not get any of your chosen Topics.",
                                      email.body)

            self.assertTrue(contains)

        term_finalization.delete()
        accepted_application1.delete()
        accepted_application2.delete()
        accepted_application3.delete()
        accepted_application4.delete()

    def test_handle_send_mail_term_not_finalized(self):

        data = {
            "action": "sendEmails"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'Term needs to be finalized')

    def test_handle_send_mail_already_send(self):

        data = {
            "action": "sendEmails"
        }

        TermFinalization.objects.create(term=self.term, finalized=True, mails_send=True)

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'Emails got already send for this Term')

    def test_handle_get_assignment_progress(self):
        automatic_assigment.running = True
        automatic_assigment.progress = 69.0
        automatic_assigment.eta = "test"

        data = {
            "action": "getAssignmentProgress"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)

        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "running": True,
            "progress": 69.0,
            "eta": "test"
        })

    def test_handle_change_term(self):
        term1 = Term.objects.create(name="SoSe22/23", active_term=False, registration_start=self.deadline,
                                    registration_deadline=self.deadline)

        data = {
            "action": "changeTerm",
            "newTerm": "SoSe22/23"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:admin_page'), data=data)

        self.assertEqual(response.status_code, 205)

        self.assertEqual(Term.objects.all().count(), 2)
        self.assertTrue(Term.objects.get(name="SoSe22/23").active_term)

        term2 = Term.objects.create(name="WiSe22", active_term=False, registration_start=self.deadline,
                                    registration_deadline=self.deadline)
        term3 = Term.objects.create(name="WiSe23", active_term=False, registration_start=self.deadline,
                                    registration_deadline=self.deadline)

        data = {
            "action": "changeTerm",
            "newTerm": "WiSe23"
        }

        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertTrue(response.status_code, 205)

        self.assertEqual(Term.objects.all().count(), 4)
        self.assertFalse(Term.objects.get(name="SoSe22/23").active_term)
        self.assertFalse(Term.objects.get(name="WiSe22").active_term)
        self.assertTrue(Term.objects.get(name="WiSe23").active_term)

        term1.delete()
        term2.delete()
        term3.delete()

    def test_handle_invalid_post(self):
        data = {
            "test": "nice"
        }

        self.client.force_login(self.superUser1)

        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"POST request didn't specify an action. Please report this and the actions you"
                         b" took to get this message to the administrator!")

        data = {
            "action": "nice"
        }

        response = self.client.post(reverse('backend:admin_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"invalid request action: nice. Please report this and the actions you took to "
                         b"get this message to an administrator!")

        response = admin_page.handle_post("invalid request")
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content.startswith(b"request caused an exception: \n "))


# noinspection DuplicatedCode,PyUnresolvedReferences,DjangoOrm
class HomePageTest(TestCase):

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
        cls.praktikum_type = CourseType.objects.create(type='Praktikum')

        cls.deadline = timezone.now()
        cls.deadline += timedelta(days=1)
        start = timezone.now()
        start -= timedelta(days=1)

        cls.term = Term.objects.create(name="WiSe22/23", active_term=True, registration_start=start,
                                       registration_deadline=cls.deadline)

        cls.course1 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course1",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course2 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course2",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB18")
        cls.course3 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=8,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course3",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course4 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=3,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course4",
                                            created_by=cls.superUser1,
                                            term=cls.term,
                                            faculty="FB20")
        cls.topic1A = Topic.objects.create(course=cls.course1, title='topic1A', max_slots=10, min_slot_size=7,
                                           max_slot_size=5)
        cls.topic1B = Topic.objects.create(course=cls.course2, title='topic1B', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2A = Topic.objects.create(course=cls.course3, title='topic2A', max_slots=3, min_slot_size=3,
                                           max_slot_size=5)
        cls.topic2B = Topic.objects.create(course=cls.course4, title='topic2B', max_slots=3, min_slot_size=1,
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

    def test_admin_page_template(self):
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:home_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend/home.html')

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the assignment view exists at the correct location.
        """
        self.client.force_login(self.superUser1)
        response = self.client.get(reverse('backend:home_page'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        response = self.client.get(reverse('backend:home_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    def test_redirect_for_default_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('backend:home_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    def test_handle_get_problems_listing(self):
        """
        Tests if the getProblemsListing action returns the correct data
        """
        data = {
            "action": "getProblemsListing"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             '{"brokenSlots": [[[1, 1, "Slot 2 of topic \\"topic1A\\" [3/5]", "Less than minimal '
                             'amount of student in this slot"]], []], "unfulfilledCollections": [["group 3", 1, 3], '
                             '["group 4", 1, 4], ["group 5", 1, 5]]}')

    def test_handle_get_chart_data(self):
        """
        Tests if the response of a getProblemsListing action is correct
        """

        data = {
            "action": "getChartData",
            "minCP": 0,
            "maxCP": 6,
            "courseTypes[]": [
                self.seminar_type.id
            ],
            "faculties[]": [
                "FB20"
            ]
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"groups": [1, 1, 0, 0, 0, 0, 1], "students": [2, 1, 0, 0, 0, 0, 1], "score": "80.38 %"})

        data = {
            "action": "getChartData",
            "minCP": -1,
            "maxCP": -1,
            "courseTypes[]": [
                self.seminar_type.id
            ],
            "faculties[]": [
                "FB20"
            ]
        }

        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'groups': [
                1,
                1,
                0,
                0,
                0,
                0,
                3
            ],
            'score': '58.26 %',
            'students': [
                2,
                1,
                0,
                0,
                0,
                0,
                3
            ]
        })

        data = {
            "action": "getChartData",
            "minCP": 0,
            "maxCP": 10,
            "courseTypes[]": [
                self.seminar_type.id,
                self.praktikum_type.id
            ],
            "faculties[]": [
                "FB18",
                "FB20"
            ]
        }

        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'groups': [
                1,
                1,
                0,
                0,
                0,
                0,
                3
            ],
            'score': '58.26 %',
            'students': [
                2,
                1,
                0,
                0,
                0,
                0,
                3
            ]
        })

    def test_handle_do_automatic_assignments(self):
        """
        Tests if the response of a do automatic assignment action is correct
        """

        automatic_assigment.iterations = 0

        data = {
            "action": "doAutomaticAssignments"
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:home_page'), data=data)

        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "status": "done"
        })

    def test_handle_clear_slot(self):
        """
        Tests if the response of a clear slot action is correct
        """

        assignment = Assignment.objects.create(topic=self.topic1A, slot_id=1)
        assignment.accepted_applications.add(self.topic_selection2)

        data = {
            "action": "clearSlot",
            "assignmentID": assignment.id
        }

        self.client.force_login(self.superUser1)
        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(Assignment.objects.filter(id=assignment.id).exists())

    def test_handle_invalid_post(self):
        """
        Tests if the response of a post is correct when it is not properly formatted
        """

        data = {
            "test": "nice"
        }

        self.client.force_login(self.superUser1)

        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"POST request didn't specify an action. Please report this and the actions you"
                         b" took to get this message to the administrator!")

        data = {
            "action": "nice"
        }

        response = self.client.post(reverse('backend:home_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"invalid request action: nice. Please report this and the actions you took to "
                         b"get this message to an administrator!")

        response = home_page.handle_post("invalid request")
        self.assertEqual(response.status_code, 500)

        self.assertTrue(response.content.startswith(b"request  caused an exception: \n "))
