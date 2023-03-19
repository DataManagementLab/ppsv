import datetime
from datetime import timedelta

from django.contrib.auth.models import User, Group as User_group
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from course.models import CourseType, Course, Topic, TopicSelection, Student, Group as Course_group, Term
from backend.models import Assignment
from teachers.pages import overview_page


# noinspection DuplicatedCode, PyUnresolvedReferences
class TeacherPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345', email="email1@test.com")
        cls.user2 = User.objects.create_user(username='testuser2', password='12345', email="email2@test.com")
        cls.user3 = User.objects.create_user(username='testuser3', password='12345', email="email3@test.com")
        cls.user4 = User.objects.create_user(username='testuser4', password='12345', email="email4@test.com")
        cls.user5 = User.objects.create_user(username='testuser5', password='12345', email="email5@test.com")
        cls.user6 = User.objects.create_user(username='testuser6', password='12345', email="email6@test.com")

        cls.teacher = User.objects.create_user(username='testteacher', password='12345')
        cls.teacher_group = User_group.objects.get(name='teacher')
        cls.teacher.groups.add(cls.teacher_group)

        cls.seminar_type = CourseType.objects.create(type='Seminar')
        cls.praktikum_type = CourseType.objects.create(type='Praktikum')

        cls.deadline = datetime.datetime(2021, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        cls.deadline += timedelta(days=1)
        start = datetime.datetime(2022, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        start -= timedelta(days=1)

        cls.term = Term.objects.create(name="WiSe22/23", active_term=True, registration_start=start,
                                       registration_deadline=cls.deadline)

        cls.course1 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course1",
                                            created_by=cls.teacher,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course2 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=5,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course2",
                                            created_by=cls.teacher,
                                            term=cls.term,
                                            faculty="FB18")
        cls.course3 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=8,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course3",
                                            created_by=cls.teacher,
                                            term=cls.term,
                                            faculty="FB20")
        cls.course4 = Course.objects.create(registration_start=start,
                                            registration_deadline=cls.deadline,
                                            cp=3,
                                            motivation_text=True,
                                            type=cls.seminar_type,
                                            title="course4",
                                            created_by=cls.teacher,
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

        cls.group1_1_2 = Course_group.objects.create()
        cls.group1_1_2.students.add(cls.student1)
        cls.group1_1_2.students.add(cls.student2)

        cls.group2_3 = Course_group.objects.create()
        cls.group2_3.students.add(cls.student3)

        cls.group3_4 = Course_group.objects.create()
        cls.group3_4.students.add(cls.student4)

        cls.group4_5 = Course_group.objects.create()
        cls.group4_5.students.add(cls.student5)

        cls.group5_6 = Course_group.objects.create()
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

    def test_teacher_page_template(self):
        """
        Tests if the correct template was used and site is reachable
        """
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('teachers:overview_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teachers/overview.html')

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the admin login page when trying to access the assignment page.
        """
        response = self.client.get(reverse('teachers:overview_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('frontend:login') + '?next=' + reverse('teachers:overview_page'))

    def test_redirect_for_default_user(self):
        """
        Tests if a default user is redirected to the admin login page when trying to access the assignment page.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('teachers:overview_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('frontend:login') + '?next=' + reverse('teachers:overview_page'))

    def test_handle_bulk_courses(self):
        """
        Tests if the getBulkCourses action returns the correct data
        """
        data = {
            "action": "getBulkCourses"
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             '{"courses": [{"id": 1, "title": "course1", "topics": [{"id": 1, "title": "topic1A", '
                             '"description": "", "nrSlots": 10, "minGroupSize": 7, "maxGroupSize": 5, "file": ""}], '
                             '"type": "Seminar", "typeID": 1, "faculty": "FB20", "term": "WiSe22/23", "term_active": '
                             'true, "startdate": "2022-12-30T23:59:59Z", "enddate": "2022-01-01T23:59:59Z", "cp": 5, '
                             '"motText": true, "description": ""}, {"id": 2, "title": "course2", "topics": [{"id": 2, '
                             '"title": "topic1B", "description": "", "nrSlots": 3, "minGroupSize": 3, "maxGroupSize": '
                             '5, "file": ""}], "type": "Seminar", "typeID": 1, "faculty": "FB18", '
                             '"term": "WiSe22/23", "term_active": true, "startdate": "2022-12-30T23:59:59Z", "enddate":'
                             '"2022-01-01T23:59:59Z", "cp": 5, "motText": true, "description": ""}, {"id": 3, '
                             '"title": "course3", "topics": [{"id": 3, "title": "topic2A", "description": "", '
                             '"nrSlots": 3, "minGroupSize": 3, "maxGroupSize": 5, "file": ""}], "type": "Seminar", '
                             '"typeID": 1, "faculty": "FB20", "term": "WiSe22/23", "term_active": true, "startdate": '
                             '"2022-12-30T23:59:59Z", "enddate": "2022-01-01T23:59:59Z", "cp": 8, "motText": true, '
                             '"description": ""}, {"id": 4, "title": "course4", "topics": [{"id": 4, '
                             '"title": "topic2B", "description": "", "nrSlots": 3, "minGroupSize": 1, "maxGroupSize": '
                             '1, "file": ""}], "type": "Seminar", "typeID": 1, "faculty": "FB20", '
                             '"term": "WiSe22/23", "term_active": true, "startdate": "2022-12-30T23:59:59Z", "enddate":'
                             '"2022-01-01T23:59:59Z", "cp": 3, "motText": true, "description": ""}]}')

    def test_handle_create_course_with_motivation(self):
        """
        Tests if the createCourse action creates a new course
        """

        action = "createCourse"
        course_title = "course5"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        course_term = self.term.id
        start_date = "2023-12-30"
        start_time = "23:59:59"
        end_date = "2024-12-30"
        end_time = "00:59:59"
        start = datetime.datetime(2023, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        end = datetime.datetime(2024, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone())
        cp = 5
        course_motivational_text = 'on'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_term_id": course_term,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        self.assertTrue(Course.objects.filter(
            title=course_title,
            type_id=course_type,
            faculty=course_faculty,
            term_id=course_term,
            registration_start=start,
            registration_deadline=end,
            cp=cp,
            motivation_text=True,
            description=course_description,
            created_by=response.wsgi_request.user
        ).exists())

    def test_handle_create_course_without_motivation(self):
        """
        Tests if the createCourse action creates a new course
        """

        action = "createCourse"
        course_title = "course5"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        course_term = self.term.id
        start_date = "2023-12-30"
        start_time = "23:59:59"
        end_date = "2024-12-30"
        end_time = "00:59:59"
        start = datetime.datetime(2023, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        end = datetime.datetime(2024, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone())
        cp = 5
        course_motivational_text = 'off'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_term_id": course_term,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        self.assertTrue(Course.objects.filter(
            title=course_title,
            type_id=course_type,
            faculty=course_faculty,
            term_id=course_term,
            registration_start=start,
            registration_deadline=end,
            cp=cp,
            motivation_text=False,
            description=course_description,
            created_by=response.wsgi_request.user
        ).exists())

    def test_handle_create_course_wrong_registration(self):
        """
        Tests if the createCourse action does not create a new course
        if the registration start is after the registration end
        """

        action = "createCourse"
        course_title = "course5"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        course_term = self.term.id
        end_date = "2023-12-30"
        end_time = "23:59:59"
        start_date = "2024-12-30"
        start_time = "00:59:59"
        cp = 5
        course_motivational_text = 'on'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_term_id": course_term,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "error", "message": "registration '
                                                                     'start must be before registration end!"}')

        self.assertFalse(Course.objects.filter(title=course_title).exists())

    def test_handle_create_topic(self):
        """
        Tests if the createTopic action creates a new topic
        """

        action = "createTopic"
        topic_title = "topic1"
        topic_course = self.course1.id
        topic_max_slots = 10
        topic_min_size = 5
        topic_max_size = 8
        topic_description = "Hello World!"
        topic_file = SimpleUploadedFile("fileName.mp4", b"file_content", content_type="video/mp4")

        data = {
            "action": action,
            "topic_title": topic_title,
            "topic_course": topic_course,
            "topic_max_slots": topic_max_slots,
            "topic_min_size": topic_min_size,
            "topic_max_size": topic_max_size,
            "topic_description": topic_description,
            "topic_file": topic_file,
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        topic_query = Topic.objects.filter(
            title=topic_title,
            course_id=topic_course,
            max_slots=topic_max_slots,
            min_slot_size=topic_min_size,
            max_slot_size=topic_max_size,
            description=topic_description,
        )

        self.assertTrue(topic_query.exists())
        self.assertTrue("fileName" in topic_query.first().file.name)
        self.assertTrue(topic_query.first().file.name.endswith(".mp4"))

    def test_handle_edit_course_with_motivation(self):
        """
        Tests if the editCourse action edits a course correctly
        """

        course = Course.objects.create(
            title="course2",
            type=self.praktikum_type,
            faculty="FB18",
            term=self.term,
            registration_start=datetime.datetime(2020, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone()),
            registration_deadline=datetime.datetime(2021, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone()),
            cp=10,
            motivation_text=True,
            description="Goodbye World!",
        )

        action = "editCourse"
        course_id = course.id
        course_title = "course1"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        start_date = "2023-12-30"
        start_time = "23:59:59"
        end_date = "2024-12-30"
        end_time = "00:59:59"
        start = datetime.datetime(2023, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        end = datetime.datetime(2024, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone())
        cp = 5
        course_motivational_text = 'off'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_id": course_id,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        course = Course.objects.get(id=course_id)

        self.assertEqual(course.title, course_title)
        self.assertEqual(course.type.id, course_type)
        self.assertEqual(course.faculty, course_faculty)
        self.assertEqual(course.registration_start, start)
        self.assertEqual(course.registration_deadline, end)
        self.assertEqual(course.cp, cp)
        self.assertEqual(course.motivation_text, False)
        self.assertEqual(course.description, course_description)

    def test_handle_edit_course_without_motivation(self):
        """
        Tests if the editCourse action edits a course correctly
        """

        course = Course.objects.create(
            title="course2",
            type=self.praktikum_type,
            faculty="FB18",
            term=self.term,
            registration_start=datetime.datetime(2020, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone()),
            registration_deadline=datetime.datetime(2021, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone()),
            cp=10,
            motivation_text=False,
            description="Goodbye World!",
        )

        action = "editCourse"
        course_id = course.id
        course_title = "course1"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        start_date = "2023-12-30"
        start_time = "23:59:59"
        end_date = "2024-12-30"
        end_time = "00:59:59"
        start = datetime.datetime(2023, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        end = datetime.datetime(2024, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone())
        cp = 5
        course_motivational_text = 'on'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_id": course_id,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        course = Course.objects.get(id=course_id)

        self.assertEqual(course.title, course_title)
        self.assertEqual(course.type.id, course_type)
        self.assertEqual(course.faculty, course_faculty)
        self.assertEqual(course.registration_start, start)
        self.assertEqual(course.registration_deadline, end)
        self.assertEqual(course.cp, cp)
        self.assertEqual(course.motivation_text, True)
        self.assertEqual(course.description, course_description)

    def test_handle_edit_course_wrong_registration(self):
        """
        Tests if the editCourse action returns an error if the registration start is after the registration end
        """

        course = Course.objects.create(
            title="course2",
            type=self.praktikum_type,
            faculty="FB18",
            term=self.term,
            registration_start=datetime.datetime(2020, 12, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone()),
            registration_deadline=datetime.datetime(2021, 12, 30, 0, 59, 59, tzinfo=timezone.get_current_timezone()),
            cp=10,
            motivation_text=True,
            description="Goodbye World!",
        )

        action = "editCourse"
        course_id = course.id
        course_title = "course1"
        course_type = self.seminar_type.id
        course_faculty = "FB20"
        end_date = "2023-12-30"
        end_time = "23:59:59"
        start_date = "2024-12-30"
        start_time = "00:59:59"
        cp = 5
        course_motivational_text = 'off'
        course_description = "Hello World!"

        data = {
            "action": action,
            "course_id": course_id,
            "course_title": course_title,
            "course_type": course_type,
            "course_faculty": course_faculty,
            "course_registration_start_date": start_date,
            "course_registration_start_time": start_time,
            "course_registration_end_date": end_date,
            "course_registration_end_time": end_time,
            "course_cp": cp,
            "course_motivational_text": course_motivational_text,
            "course_description": course_description
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "error", "message": "registration '
                                                                     'start must be before registration end!"}')

    def test_handle_edit_topic(self):
        """
        Tests if the editTopic action edits a topic correctly
        """

        topic = Topic.objects.create(
            course=self.course1,
            title="topic1",
            max_slots=10,
            min_slot_size=1,
            max_slot_size=3,
            description="Goodbye World!",
            file=SimpleUploadedFile("fileName.mp4", b"file_content", content_type="video/mp4")
        )

        action = "editTopic"
        topic_id = topic.id
        topic_title = "topic2"
        topic_max_slots = 5
        topic_min_slot_size = 2
        topic_max_slot_size = 4
        topic_description = "Hello World!"
        topic_file = SimpleUploadedFile("fileName2.mp4", b"file_content", content_type="video/mp4")

        data = {
            "action": action,
            "topic_id": topic_id,
            "topic_title": topic_title,
            "topic_course": self.course2.id,
            "topic_max_slots": topic_max_slots,
            "topic_min_size": topic_min_slot_size,
            "topic_max_size": topic_max_slot_size,
            "topic_description": topic_description,
            "topic_file": topic_file
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"status": "success"}')

        topic = Topic.objects.get(id=topic_id)

        self.assertEqual(topic.title, topic_title)
        self.assertEqual(topic.course, self.course2)
        self.assertEqual(topic.max_slots, topic_max_slots)
        self.assertEqual(topic.min_slot_size, topic_min_slot_size)
        self.assertEqual(topic.max_slot_size, topic_max_slot_size)
        self.assertEqual(topic.description, topic_description)
        self.assertTrue("fileName2" in topic.file.name)
        self.assertTrue(topic.file.name.endswith(".mp4"))

    def test_handle_select_topic(self):
        """
        Tests if the selectTopic action selects a topic correctly
        """

        data = {
            "action": "selectTopic",
            "topicID": self.topic1A.id
        }

        self.client.force_login(self.teacher)
        response = self.client.post(reverse('teachers:overview_page'), data=data)
        print(response.content)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             '{"topicMinSlotSize": 7, "topicMaxSlotSize": 5, "slots": [{"slotID": 1, "groups": [], '
                             '"studentCount": 0}, {"slotID": 2, "groups": [["  &lt&gt", "  &lt&gt"], ["  &lt&gt"]], '
                             '"studentCount": 3}, {"slotID": 3, "groups": [], "studentCount": 0}, {"slotID": 4, '
                             '"groups": [], "studentCount": 0}, {"slotID": 5, "groups": [], "studentCount": 0}, '
                             '{"slotID": 6, "groups": [], "studentCount": 0}, {"slotID": 7, "groups": [], '
                             '"studentCount": 0}, {"slotID": 8, "groups": [], "studentCount": 0}, {"slotID": 9, '
                             '"groups": [], "studentCount": 0}, {"slotID": 10, "groups": [], "studentCount": 0}], '
                             '"unassignedGroups": [["  &lt&gt"]]}')

    def test_handle_invalid_post(self):
        """
        Tests if the response of a post is correct when it is not properly formatted
        """

        data = {
            "test": "nice"
        }

        self.client.force_login(self.teacher)

        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"POST request didn't specify an action. Please report this and the actions you"
                         b" took to get this message to the administrator!")

        data = {
            "action": "nice"
        }

        response = self.client.post(reverse('teachers:overview_page'), data=data)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.content,
                         b"invalid request action: nice. Please report this and the actions you took to "
                         b"get this message to an administrator!")

        response = overview_page.handle_post("invalid request")
        self.assertEqual(response.status_code, 500)

        self.assertTrue(response.content.startswith(b"request  caused an exception: \n "))
