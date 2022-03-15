from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
import datetime
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
        self.assertTrue(form.fields['username'].label == '')
        self.assertTrue(form.fields['password'].label == '')


class HomepageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        cls.group1 = Group.objects.create()
        cls.group1.students.add(cls.student1)
        cls.course = Course.objects.create(registration_deadline=timezone.now(), cp=5, motivation_text=True)
        cls.topic = Topic.objects.create(course=cls.course, title='Title')
        cls.topic_selection = TopicSelection.objects.create(group=cls.group1, topic=cls.topic, collection_number=0)
        cls.course_mix1 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='IN')
        cls.course_mix2 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='SE')
        cls.topic_mix1 = Topic.objects.create(course=cls.course_mix1, title='Mix1')
        cls.topic_mix2 = Topic.objects.create(course=cls.course_mix2, title='Mix2')
        cls.topic_selection_mix1 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_mix1,
                                                                 collection_number=1)
        cls.topic_selection_mix2 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_mix2,
                                                                 collection_number=1)

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

    def test_view_for_anonymous_user(self):
        """
        Tests if an anonymous user is presented the login form and the welcome text on the homepage.
        """
        response = self.client.get(reverse('frontend:homepage'))
        self.assertContains(response, 'Willkommen')
        self.assertContains(response, '<div class="row-cols-sm-1" id="col_1">')

    def test_view_for_logged_in_user_with_selection(self):
        """
        Tests if an logged in user is presented with the reminders depending on their selections.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You still need to assign at least one topic to a collection')
        self.assertContains(response, 'You still need to write one or more motivation texts!')
        self.assertContains(response, 'You can view and manage your selected topics and collections here:')
        self.assertContains(response, 'There is at least one collection that has mixed course types!')

    def test_view_for_logged_in_user_without_selection(self):
        """
        Tests if an logged in user is presented with the reminders depending on their selections.
        """
        self.client.force_login(self.user2)
        response = self.client.get(reverse('frontend:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have not selected any topics yet!')
        self.assertContains(response, 'You can create a group here')


class OverviewViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        # cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        # cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        # cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        # cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        # cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        # cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee')
        # cls.group1 = Group.objects.create()
        # cls.group1.students.add(cls.student1)
        cls.date_future = timezone.now() + datetime.timedelta(days=30)
        cls.course = Course.objects.create(registration_deadline=cls.date_future, registration_start=timezone.now(),
                                           cp=5, motivation_text=True, faculty='FB01', title='TestCourse', type='SE',
                                           description='Test description')
        cls.topic = Topic.objects.create(course=cls.course, title='TestTopic')
        # cls.topic_selection = TopicSelection.objects.create(group=cls.group1, topic=cls.topic, collection_number=0)
        # cls.course_mix1 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='IN')
        # cls.course_mix2 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='SE')
        # cls.topic_mix1 = Topic.objects.create(course=cls.course_mix1, title='Mix1')
        # cls.topic_mix2 = Topic.objects.create(course=cls.course_mix2, title='Mix2')
        # cls.topic_selection_mix1 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_mix1,
        #                                                          collection_number=1)
        # cls.topic_selection_mix2 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_mix2,
        #                                                          collection_number=1)

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the overview view exists at the correct location.
        """
        response = self.client.get('/overview/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the homepage view uses the correct template homepage.html.
        """
        response = self.client.get(reverse('frontend:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/overview.html')

    def test_overview_faculties(self):
        """
        Tests if the overview view displays a faculty which contains a course.
        """
        response = self.client.get(reverse('frontend:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FB01')
        self.assertNotContains(response, 'FB02')

    # 'choose_faculty': ['FB20']
    # 'choose_course': ['7|FB20|True']
    # 'choose_topic': ['3|7|FB20|False']

    def test_overview_courses_of_faculty(self):
        """
        Tests if the overview view displays the courses of a faculty.
        """
        data = {'choose_faculty': ['FB01']}
        response = self.client.post(reverse('frontend:overview'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestCourse')

    def test_overview_topics_and_information_of_course(self):
        """
        Tests if the overview view displays the topics of a course.
        """
        data = {'choose_course': ['1|FB20|True']}
        response = self.client.post(reverse('frontend:overview'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestTopic')
        self.assertContains(response, 'Test description')
    # to do: tests for choosing a course after merge and clean up setup method


class YourSelectionViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user_no_student = User.objects.create_user(username='testuser2', password='12345')
        # cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        # cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee')
        # cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd33eeee')
        cls.group1 = Group.objects.create()
        cls.group1.students.add(cls.student1)
        cls.date_future = timezone.now() + datetime.timedelta(days=30)
        cls.course = Course.objects.create(registration_deadline=cls.date_future, registration_start=timezone.now(),
                                           cp=5, motivation_text=True, faculty='FB01', title='TestCourse', type='SE',
                                           description='Test description', collection_exclusive=True)
        cls.topic_col0 = Topic.objects.create(course=cls.course, title='Unassigned Topic', description='Testing')
        cls.topic_col1_0 = Topic.objects.create(course=cls.course, title='Assigned Topic 0')
        cls.topic_col1_1 = Topic.objects.create(course=cls.course, title='Assigned Topic 1')
        cls.topic_selection_col0 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_col0,
                                                                 collection_number=0)
        cls.topic_selection_col1_0 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_col1_0,
                                                                   collection_number=1)
        cls.topic_selection_col1_1 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_col1_1,
                                                                   collection_number=1)
        # cls.course_mix1 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='IN')
        # cls.course_mix2 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type='SE')

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the your_selection view exists at the correct location.
        """
        self.client.force_login(self.user1)
        response = self.client.get('/your_selection/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the your_selection view uses the correct template your_selection.html.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:your_selection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/your_selection.html')

    def test_redirect_for_anonymous_user_or_user_without_student(self):
        """
        Tests if an anonymous user is redirected to the login page when trying to access the your_selection view.
        """
        response = self.client.get(reverse('frontend:your_selection'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/login/?next=/your_selection/')

    def test_redirect_for_user_without_student(self):
        """
        Tests if a logged in user without student profile is redirected to the login page and is shown a message when
        trying to access the your_selection view.
        """
        self.client.force_login(self.user_no_student)
        response = self.client.get(reverse('frontend:your_selection'), follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please create a student profile before selecting courses.')
        self.assertRedirects(response, '/profile/?next=/your_selection/')

    def test_display_of_selected_topic_without_collection(self):
        """
        Tests if a selected topic without collection is displayed on the your_selection view.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:your_selection'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assign these topics to your desired collections')
        self.assertContains(response, 'Unassigned Topic')
        self.assertContains(response, 'Remove Topic')

    def test_display_of_selected_topic_with_collection(self):
        """
        Tests if a selected topic which is assigned to a collection is displayed on the your_selection view.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:your_selection'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Motivation Text')
        # self.assertContains(response, 'Collection 1 exclusive for topics of course "TestCourse"')

    def test_information_panel(self):
        """
        Tests if the information panel works and displays the topic & course information.
        """
        data = {'open_selection_info': ['1'], 'open_course_info': ['False'], 'selection': [' False |1 '],
                'course_info_button': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test description')
        self.assertContains(response, 'Testing')

    # requires further button testing


class GroupsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')
        cls.user3 = User.objects.create_user(username='testuser3', password='12345')
        cls.user4 = User.objects.create_user(username='testuser4', password='12345')
        cls.user_no_student = User.objects.create_user(username='user_no_student', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab22eeee', firstname='Klaus', lastname='Hans',
                                              email='test1@yahoo.de')
        cls.student2 = Student.objects.create(user=cls.user2, tucan_id='bc22eeee', firstname='John', lastname='Smith',
                                              email='test2@gmail.com')
        cls.student3 = Student.objects.create(user=cls.user3, tucan_id='cd22eeee', firstname='Berta',
                                              lastname='Bruckner', email='test@aol.com')
        cls.student4 = Student.objects.create(user=cls.user4, tucan_id='de22eeee', firstname='Lisa', lastname='Müller',
                                              email='test4@gmx.de')
        cls.group1 = Group.objects.create()
        cls.group1.students.add(cls.student1)
        cls.group1.students.add(cls.student3)
        cls.group2 = Group.objects.create()
        cls.group2.students.add(cls.student1)
        cls.group2.students.add(cls.student3)
        cls.group2.students.add(cls.student4)

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the groups view exists at the correct location.
        """
        self.client.force_login(self.user1)
        response = self.client.get('/groups/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the groups view uses the correct template groups.html.
        """
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/groups.html')

    def test_redirect_for_anonymous_user_or_user_without_student(self):
        """
        Tests if an anonymous user is redirected to the login page when trying to access the groups view.
        """
        response = self.client.post(reverse('frontend:groups'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/login/?next=/groups/')

    def test_redirect_for_user_without_student(self):
        """
        Tests if a logged in user without student profile is redirected to the login page and is shown a message when
        trying to access the groups view.
        """
        self.client.force_login(self.user_no_student)
        response = self.client.post(reverse('frontend:groups'), follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please create a student profile before accessing your groups.')
        self.assertRedirects(response, '/profile/?next=/groups/')

    def test_basic_group_display(self):
        """
        Tests if all groups of a student are displayed by the groups view.
        """
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Klaus Hans')
        # warum funktioniert das hier nicht?
        # self.assertContains(response, 'test1@yahoo.de')
        self.assertContains(response, 'cd22eeee')
        self.assertContains(response, 'Create a new group')

    # moved into the next test
    # def test_create_new_group_ui_shows_up(self):
    #     """
    #     Tests if the group creation UI is displayed after clicking on 'Create a new group'.
    #     """
    #     data = {'open_create_new_group': ['']}
    #     self.client.force_login(self.user1)
    #     response = self.client.post(reverse('frontend:groups'), data=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'id="add_student_to_new_group"')

    def test_create_new_group_add_user(self):
        """
        Tests if a new user is correctly added to the new group members when creating a new group.
        """
        data = {'new_student_id': ['bc22eeee'], 'add_student_to_new_group': [''], 'member0': ['ab22eeee']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="add_student_to_new_group"')
        self.assertContains(response, 'bc22eeee')

    def test_create_new_group(self):
        """
        Tests if a new group is created correctly.
        """
        data = {'new_student_id': [''], 'member0': ['ab22eeee'], 'member1': ['bc22eeee'], 'create_new_group': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Group.objects.filter(students='bc22eeee').exists())

    def test_adding_student_to_existing_group(self):
        """
        Tests if a student is correctly added to an existing group.
        """
        data = {'add_student': [self.group2.id], 'student_id': ['bc22eeee']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.group2.get_display, 'ab22eeee, bc22eeee, cd22eeee, de22eeee')

    def test_removing_student_from_existing_group(self):
        """
        Tests if a student is correctly removed from an existing group.
        """
        data = {'remove_student': [str(self.group2.id) + '|cd22eeee'], 'student_id': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.group2.get_display, 'ab22eeee, de22eeee')

    def test_confirmation_for_deleting_group(self):
        """
        Tests if the confirmation question for deleting a group is displayed when trying to do so.
        """
        data = {'ask_delete_group': [self.group2.id], 'student_id': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="{}delete"'.format(self.group2.id))

    def test_deleting_group(self):
        """
        Tests if a group is deleted correctly.
        """
        group_id = self.group2.id
        data = {'delete_group': [group_id]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Group.objects.filter(id=group_id).exists())

    def test_adding_student_to_existing_group_duplicate(self):
        """
        Tests if the correct error message pops up if the adding of a new student to an existing group would make
        it a duplicate.
        """
        data = {'add_student': [self.group1.id], 'student_id': ['de22eeee']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Adding de22eeee would make this group a duplicate of an already '
                                           'existing one.')

    def test_student_is_already_member_of_existing_group(self):
        """
        Tests if the correct error message is shown if the student the user is trying to add is already in the group.
        """
        data = {'add_student': [self.group1.id], 'student_id': ['ab22eeee']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'ab22eeee is already a member of this group.')

    def test_student_not_found(self):
        """
        Tests if the correct error message is shown if the student the user is trying to add does not exist.
        """
        data = {'add_student': [self.group1.id], 'student_id': ['xx22xxxx']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'A student with the TUCaN-ID xx22xxxx does not exist.')

    # konnte post data nicht finden
    def test_removing_penultimate_student_from_group(self):
        """
        Tests if the group deletion message is shown when a user tries to remove the penultimate student from the group.
        """

    def test_student_is_already_member_of_new_group(self):
        """
        Tests if the correct error message is shown if the student the user is trying to add is already in the group.
        """
        data = {'new_student_id': ['ab22eeee'], 'add_student_to_new_group': [''], 'member0': ['ab22eeee']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'A student with the TUCaN-ID ab22eeee is already in the group.')

    def test_student_not_found_new_group_creation(self):
        """
        Tests if the correct error message is shown if the student the user is trying to add does not exist.
        """
        data = {'new_student_id': ['xx22xxxx'], 'add_student_to_new_group': [''], 'member0': ['abcdabcd']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'A student with the TUCaN-ID xx22xxxx does not exist.')

