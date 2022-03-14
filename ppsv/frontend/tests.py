from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
import datetime
from django.test import TestCase
from django.utils import timezone
from course.models import Course, Student, Group, Topic, TopicSelection
from .forms.forms import NewStudentForm, NewUserForm, UserLoginForm
from django.utils.safestring import mark_safe
from django.utils.functional import lazy


class FormTests(TestCase):
    def test_new_student_form_labels(self):
        """
        Tests if the labels of the input fields are correct.
        """
        form = NewStudentForm()
        self.assertTrue(form.fields['tucan_id'].label == '')
        self.assertTrue(form.fields['firstname'].label == '')
        self.assertTrue(form.fields['lastname'].label == '')

    def test_new_student_form_tucan_id_length(self):
        """
        Tests inputs other than eight in the tucan-id input field.
        """
        tucan_id1 = 'aa22bb'
        tucan_id2 = '999999999'
        tucan_id3 = 'bb88abcd'
        first_name = 'Hans'
        last_name = 'Hans'
        form = NewStudentForm(data={'tucan_id': tucan_id1, 'firstname': first_name, 'lastname': last_name})
        self.assertFalse(form.is_valid())
        form = NewStudentForm(data={'tucan_id': tucan_id2, 'firstname': first_name, 'lastname': last_name})
        self.assertFalse(form.is_valid())
        form = NewStudentForm(data={'tucan_id': tucan_id3, 'firstname': first_name, 'lastname': last_name})
        self.assertTrue(form.is_valid())

    def test_new_user_form_labels(self):
        """
        Tests if the labels of the input fields are correct.
        """
        form = NewUserForm()
        self.assertTrue(form.fields['email'].label == '')
        self.assertTrue(form.fields['username'].label == '')
        self.assertTrue(form.fields['password1'].label == '')
        self.assertTrue(form.fields['password2'].label == '')

    def test_new_user_form_help_text(self):
        """
        Tests if the help texts of the input fields are correct.
        """
        form = NewUserForm()
        mark_safe_lazy = lazy(mark_safe, str)
        self.assertTrue(form.fields['username'].help_text == mark_safe_lazy(
            "<div style=\"padding-left: 10px\"><small>Letters, numbers and @/./+/-/_ only."
            "</small></div>"))
        self.assertTrue(form.fields['password2'].help_text == mark_safe_lazy(
            "<div style=\"padding-left: 10px\"><small>"
            "The password must not contain any personal information.<br>"
            "The password has to be at least 8 digits long.<br>"
            "The password must not be commonly used.<br>"
            "The password must not contain only numbers.</small></div>"))

    def test_user_login_form_labels(self):
        """
        Tests if the labels of the input fields are correct.
        """
        form = UserLoginForm()
        self.assertTrue(form.fields['username'].label is '')
        self.assertTrue(form.fields['password'].label is '')


class HomepageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        # self.user2 = User.objects.create_user(username='testuser2', password='12345')
        # self.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        # self.student2 = Student.objects.create(user=self.user2, tucan_id='bc22eeee')
        # self.student3 = Student.objects.create(user=self.user3, tucan_id='cd33eeee')
        cls.group1 = Group.objects.create()
        cls.group1.students.add(cls.student1)
        cls.course = Course.objects.create(registration_deadline=timezone.now(), cp=5)
        cls.topic = Topic.objects.create(course=cls.course, title='Title')
        cls.topic_selection = TopicSelection.objects.create(group=cls.group1, topic=cls.topic, collection_number=0)

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the homepage view exists at the correct location.
        """
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the homepage view uses the correct template homepage.html.
        """
        response = self.client.get(reverse('frontend:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/homepage.html')

    # TODO: Ist der Test korrekt, um zu checken, ob das login form angezeigt wird?
    def test_view_for_anonymous_user(self):
        """
        Tests if an anonymous user is presented the login form and the welcome text on the homepage.
        """
        response = self.client.get(reverse('frontend:homepage'))
        self.assertContains(response, 'Willkommen')
        self.assertContains(response, '<div class="row-cols-sm-1" id="col_1">')

    # TODO: other reminders
    def test_view_for_logged_in_user(self):
        """
        Tests if an logged in user is presented with the reminders depending on their selections.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You still need to assign at least one topic to a collection')


# def create_course(title, type, registration_start, registration_deadline, description, unlimited, max_participants,
#                   cp, faculty, motivation_text, organizer):
#     """
#     Create a course with the given attributes
#     """
#     # time = timezone.now() + datetime.timedelta(days=days)
#     return Course.objects.create(title=title, type=type, registration_start=registration_start,
#                                  registration_deadline=registration_deadline, description=description,
#                                  unlimited=unlimited, max_participants=max_participants, cp=cp, faculty=faculty,
#                                  motivation_text=motivation_text, organizer=organizer)


# class CourseOverviewViewTests(TestCase):
#     def test_no_questions(self):
#         """
#         If no questions exist, an appropriate message is displayed.
#         """
#         response = self.client.get(reverse('polls:index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])
#
#     def test_past_question(self):
#         """
#         Questions with a pub_date in the past are displayed on the
#         index page.
#         """
#         question = create_question(question_text="Past question.", days=-30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             [question],
#         )
#
#     def test_future_question(self):
#         """
#         Questions with a pub_date in the future aren't displayed on
#         the index page.
#         """
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])
#
#     def test_future_question_and_past_question(self):
#         """
#         Even if both past and future questions exist, only past questions
#         are displayed.
#         """
#         question = create_question(question_text="Past question.", days=-30)
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             [question],
#         )
#
#     def test_two_past_questions(self):
#         """
#         The questions index page may display multiple questions.
#         """
#         question1 = create_question(question_text="Past question 1.", days=-30)
#         question2 = create_question(question_text="Past question 2.", days=-5)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             [question2, question1],
#         )

# only as an example
# class CourseIndexViewTests(TestCase):
#     def test_page_response(self):
#         """
#         check response
#         """
#         response = self.client.get(reverse('index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Hello, world. You're at the course view.")
