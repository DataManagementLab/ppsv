from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
import datetime
from course.models import Course, Student, Group, Topic, TopicSelection, CourseType
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
        cls.seminar_type = CourseType.objects.create(type='Seminar')
        cls.internship_type = CourseType.objects.create(type='Internship')
        cls.course = Course.objects.create(registration_deadline=timezone.now(), cp=5, motivation_text=True,
                                           type=cls.seminar_type)
        cls.topic = Topic.objects.create(course=cls.course, title='Title')
        cls.topic_selection = TopicSelection.objects.create(group=cls.group1, topic=cls.topic, collection_number=0)
        cls.course_mix1 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type=cls.seminar_type)
        cls.course_mix2 = Course.objects.create(registration_deadline=timezone.now(), cp=5, type=cls.internship_type)
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
        cls.course_type = CourseType.objects.create(type='Testtype')
        cls.course = Course.objects.create(registration_deadline=cls.date_future, registration_start=timezone.now(),
                                           cp=5, motivation_text=True, faculty='FB01', title='TestCourse',
                                           type=cls.course_type, description='Test description')
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

    def test_display_faculties(self):
        """
        Tests if the overview view displays a faculty which contains a course.
        """
        response = self.client.get(reverse('frontend:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FB01')
        self.assertNotContains(response, 'FB02')

    def test_display_courses_of_faculty(self):
        """
        Tests if the overview view displays the courses of a faculty.
        """
        data = {'choose_faculty': ['FB01']}
        response = self.client.post(reverse('frontend:overview'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestCourse')
        # 'choose_faculty': ['FB01']

    def test_display_topics_and_information_of_course(self):
        """
        Tests if the overview view displays the topics of a course.
        """
        data = {'choose_course': ['1|FB20|True']}
        response = self.client.post(reverse('frontend:overview'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestTopic')
        self.assertContains(response, 'Test description')
        # 'choose_course': ['7|FB01|True']

    def test_display_topic_information_with_select_buttons(self):
        """
        Tests if the topic information and selection buttons are displayed correctly.
        """
        # 'choose_topic': ['22|7|FB01|False']

    def test_course_info_panel_in_topic(self):
        """
        Tests if the course info panel displays the information correctly if opened.
        """
        # 'choose_topic': ['22|7|FB01|True']

    def test_select_topic_without_group(self):
        """
        Tests if a topic selection without a group is working as intended.
        """
        # 'select_topic': ['22|7|FB01|open_course_info']}>select_topic alone

    def test_display_of_select_all_remaining_topic_button(self):
        """
        Tests if the button to select all remaining topics shows up after selecting one topic of a course.
        """
        # 'choose_course': ['7|FB01|False'] same as topics of course but with one topic selected and containing the button

    def test_select_all_remaining_topics(self):
        """
        Tests if all other topics of a course are correctly selected after selecting all remaining topics.
        """
        # 'select_all_remaining_topics': ['7|FB01|open_course_info']

    def test_select_all_remaining_topics(self):
        """
        Tests if the faculty view works properly after going back.
        """
        # 'faculty_view': ['']

    def test_sorting(self):
        """
        Tests if the sort function while displaying courses of a faculty works correctly.
        """
        # how? idk
        # 'choose_faculty': ['FB02|cp|dsc']

    def test_select_topic_as_group(self):
        """
        Tests if the options to create a new group and to select the topic with an existing group are presented after
        clicking select topic as a group.
        """
        # 'open_group_select': ['15|4|FB20|open_course_info']}>open_group_select, choosing topic as a group

    def test_create_new_group_ui(self):
        """
        Tests if the UI for creating a new group is displayed.
        """
        # 'open_group_create': ['15|4|FB20|False'], 'group_options': ['-1']}>open_group_create create a new group

    def test_adding_student_to_group(self):
        """
        Tests if a student is properly added to the new group.
        """
        # 'new_student_id': ['bcbcbcbc'], 'add_student': ['15|4|FB20|open_course_info'], 'member0': ['abcdabcd']}>add_student to new group draft

    def test_adding_student_to_group_draft(self):
        """
        Tests if a student is properly added to the group draft.
        """
        # 'new_student_id': ['bcbcbcbc'], 'add_student': ['15|4|FB20|open_course_info'], 'member0': ['abcdabcd']}>add_student to new group draft

    def test_removing_student_from_group_draft(self):
        """
        Tests if a student is properly removed from the group draft.
        """
        # 'new_student_id': [''], 'remove_student': ['15|4|FB20|open_course_info|bcbcbcbc'], 'member0': ['bcbcbcbc'], 'member1': ['abcdabcd']}>remove_student from group draft

    def test_select_topic_with_new_group(self):
        """
        Tests if topic is correctly selected when selecting with a newly created group.
        """
        # 'new_student_id': [''], 'select_with_new_group': ['15|4|FB20|open_course_info'], 'member0': ['bcbcbcbc'], 'member1': ['abcdabcd']}>select_with_new_group


class YourSelectionViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.user_no_student = User.objects.create_user(username='testuser2', password='12345')
        cls.student1 = Student.objects.create(user=cls.user1, tucan_id='ab12eeee')
        cls.group1 = Group.objects.create(collection_count=2)
        cls.group1.students.add(cls.student1)
        cls.date_future = timezone.now() + datetime.timedelta(days=30)
        cls.course_type = CourseType.objects.create(type='Testtype')
        cls.course = Course.objects.create(registration_deadline=cls.date_future, registration_start=timezone.now(),
                                           cp=5, motivation_text=True, faculty='FB01', title='TestCourse',
                                           type=cls.course_type, description='Test description',
                                           collection_exclusive=False)
        cls.course1 = Course.objects.create(registration_deadline=cls.date_future, registration_start=timezone.now(),
                                            cp=5, motivation_text=True, faculty='FB01', title='TestCourse1',
                                            type=cls.course_type, description='Test description 1',
                                            collection_exclusive=False)
        cls.course_exclusive = Course.objects.create(registration_deadline=cls.date_future,
                                                     registration_start=timezone.now(), cp=6, motivation_text=True,
                                                     faculty='FB02', title='TestCourse exklusiv', type=cls.course_type,
                                                     description='Test description exklusiv', collection_exclusive=True)
        cls.topic_unassigned0 = Topic.objects.create(course=cls.course, title='Unassigned Topic 0',
                                                     description='Testing unassigned 0')
        cls.topic_unassigned1 = Topic.objects.create(course=cls.course, title='Unassigned Topic 1',
                                                     description='Testing unassigned 1')
        cls.topic_col1_exclusive0 = Topic.objects.create(course=cls.course_exclusive, title='Assigned Excl. Topic 0')
        cls.topic_col1_exclusive1 = Topic.objects.create(course=cls.course_exclusive, title='Assigned Excl. Topic 1')
        cls.topic_selection_unassigned0 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_unassigned0,
                                                                        collection_number=0)
        cls.topic_selection_unassigned1 = TopicSelection.objects.create(group=cls.group1, topic=cls.topic_unassigned1,
                                                                        collection_number=0)
        cls.topic_selection_exclusive0 = TopicSelection.objects.create(group=cls.group1,
                                                                       topic=cls.topic_col1_exclusive0,
                                                                       collection_number=1)
        cls.topic_selection_exclusive1 = TopicSelection.objects.create(group=cls.group1,
                                                                       topic=cls.topic_col1_exclusive1,
                                                                       collection_number=1)

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

    def test_redirect_for_anonymous_user(self):
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
        self.assertContains(response, 'class="fa fa-exclamation-triangle" aria-hidden="true"')

    def test_display_of_selected_topic_with_collection(self):
        """
        Tests if a selected topic which is assigned to a collection is displayed on the your_selection view.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:your_selection'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Motivation Text')
        self.assertContains(response, 'exclusive for topics of course')
        self.assertContains(response, 'Assigned Excl. Topic 0')

    def test_information_panel(self):
        """
        Tests if the information panel works and displays the topic & course information.
        """
        selection_id = self.topic_selection_unassigned0.id
        data = {'open_selection_info': ['{}'.format(selection_id)], 'open_course_info': ['False'],
                'selection': [' False |{} '.format(selection_id)], 'course_info_button': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test description')
        self.assertContains(response, 'Testing unassigned 0')

    def test_remove_topic(self):
        """
        Tests if a topic is correctly removed from collection 0.
        """
        selection_id = self.topic_selection_unassigned0.id
        data = {'collection_input{}'.format(selection_id): ['0'], 'remove_topic_button': ['{}|0'.format(selection_id)]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TopicSelection.objects.filter(id=selection_id).exists())

    def test_moving_topic_to_collection(self):
        """
        Tests if a topic is moved to the correct collection when confirming the selected collection choice.
        """
        selection_id = self.topic_selection_unassigned0.id
        group_id = self.group1.id
        data = {'collection_input{}'.format(selection_id): ['2'],
                'change_collection_button': ['{}|0|{}'.format(group_id, selection_id)]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TopicSelection.objects.get(id=selection_id).collection_number, 2)

    def test_assigned_multiple_topics_of_the_same_course_to_selection(self):
        """
        Tests if multiple unassigned topics of the same course are moved to the correct collection when confirming
        the selected collection choice.
        """
        selection_id0 = self.topic_selection_unassigned0.id
        selection_id1 = self.topic_selection_unassigned1.id
        group_id = self.group1.id
        data = {'collection_input{}'.format(selection_id0): ['2'], 'collection_input{}'.format(selection_id1): ['2'],
                'change_collection_button': ['{}|0|{}'.format(group_id, selection_id0)]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TopicSelection.objects.get(id=selection_id0).collection_number, 2)
        self.assertEqual(TopicSelection.objects.get(id=selection_id1).collection_number, 2)

    def test_editing_collection(self):
        """
        Tests if all buttons are displayed when editing a collection.
        """
        group_id = self.group1.id
        data = {'open_edit_collection': ['{}'.format(group_id)]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="add_collection"')
        self.assertContains(response, 'spinning-icon')
        self.assertContains(response, 'name="remove_collection"')

    def test_ask_remove_collection(self):
        """
        Tests if a message is displayed correctly when a user is trying to delete a filled collection.
        """
        selection_id0 = self.topic_selection_exclusive0.id
        selection_id1 = self.topic_selection_exclusive1.id
        group_id = self.group1.id
        data = {'ask_remove_collection': ['{}|1'.format(group_id)], 'collection_input{}'.format(selection_id0): ['1'],
                'collection_input{}'.format(selection_id1): ['1']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'If you delete this collection, all the selections will be deleted as well.')
        self.assertContains(response, 'name="remove_collection"')

    def test_remove_collection(self):
        """
        Tests if a collection is correctly deleted.
        """
        selection_id0 = self.topic_selection_exclusive0.id
        selection_id1 = self.topic_selection_exclusive1.id
        group_id = self.group1.id
        data = {'remove_collection': ['{}|1'.format(group_id)], 'collection_input{}'.format(selection_id0): ['1'],
                'collection_input{}'.format(selection_id1): ['1']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Assigned Excl. Topic 0')
        self.assertFalse(TopicSelection.objects.filter(topic=self.topic_col1_exclusive0).exists())

    def test_adding_collection(self):
        """
        Tests if a collection is correctly added.
        """
        group_id = self.group1.id
        data = {'add_collection': ['{}'.format(group_id)]}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collection 4')

    def test_edit_motivation_text(self):
        """
        Tests if the field for the motivation text and the corresponding buttons are displayed when the user wants to
        edit the motivation text.
        """
        selection_id = self.topic_selection_exclusive0.id
        data = {'edit_motivation_text_button': ['{}'.format(selection_id)],
                'collection_input{}'.format(selection_id): ['1']
                }
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="save_motivation_text_button"')
        self.assertContains(response, 'name="cancel_motivation_save"')

    def test_save_motivation_text(self):
        """
        Tests if the motivation text is correctly saved.
        """
        selection_id = self.topic_selection_exclusive0.id
        data = {'save_motivation_text_button': ['{}'.format(selection_id)],
                'collection_input{}'.format(selection_id): ['1'],
                'motivation_text': ['Test Text']
                }
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:your_selection'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TopicSelection.objects.filter(motivation='Test Text').exists())


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
        self.assertContains(response, 'test1@yahoo.de')
        self.assertContains(response, 'cd22eeee')
        self.assertContains(response, 'Create a new group')

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

    def test_removing_penultimate_student_from_group(self):
        """
        Tests if the group deletion message is shown when a user tries to remove the penultimate student from the group.
        """
        group_id = self.group1.id
        data = {'ask_remove_student': ['{}|cd22eeee'.format(group_id)], 'student_id': ['']}
        self.client.force_login(self.user1)
        response = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'If you remove this member, your group will be too small and will be deleted.')
        self.assertContains(response, 'name="delete_group"')

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

    def test_parallel_group_deletion(self):
        """
        Tests if two users can delete the group simultaneously.
        """
        group_id = self.group1.id
        data = {'delete_group': [group_id]}
        self.client.force_login(self.user1)
        response1 = self.client.post(reverse('frontend:groups'), data=data)
        self.assertFalse(Group.objects.filter(id=group_id).exists())
        self.assertEqual(response1.status_code, 200)
        self.client.logout()
        self.client.force_login(self.user3)
        response2 = self.client.post(reverse('frontend:groups'), data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(Group.objects.filter(id=group_id).exists())

class LoginViewTests(TestCase):

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the login view exists at the correct location.
        """

        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the login view uses the correct template login.html.
        """
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_interface(self):
        """
        Tests if the login view displays the correct interface to either login or register
        """
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
        self.assertContains(response, 'I don\'t have an account.')


class RegisterViewTests(TestCase):

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the register view exists at the correct location.
        """

        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the register view uses the correct template register.html.
        """
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_interface(self):
        """
        Tests if the register view displays the correct interface to create an account
        """
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create an account')
        self.assertContains(response, 'The password must not contain any personal information.')
        self.assertContains(response, 'If you already have an account')

class ProfileViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the profile view exists at the correct location.
        """
        self.client.force_login(self.user1)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the profile view uses the correct template profile.html.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/profile.html')

    def test_register_interface(self):
        """
        Tests if the profile view displays the correct interface to create a profile / student account
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your student profile')
        self.assertContains(response, 'This information cannot be changed later!')
        self.assertContains(response, 'Save profile permanently')

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the login page when trying to access the profile view.
        """
        response = self.client.get(reverse('frontend:profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/login/?next=/profile/')


class LoginViewTests(TestCase):

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the login view exists at the correct location.
        """

        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the login view uses the correct template login.html.
        """
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_interface(self):
        """
        Tests if the login view displays the correct interface to either login or register.
        """
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
        self.assertContains(response, 'I don\'t have an account.')


class RegisterViewTests(TestCase):

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the register view exists at the correct location.
        """

        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the register view uses the correct template register.html.
        """
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_interface(self):
        """
        Tests if the register view displays the correct interface to create an account.
        """
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create an account')
        self.assertContains(response, 'The password must not contain any personal information.')
        self.assertContains(response, 'If you already have an account')


class ProfileViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data.
        """
        cls.user1 = User.objects.create_user(username='testuser1', password='12345')

    def test_view_url_exists_at_correct_location(self):
        """
        Tests if the URL of the profile view exists at the correct location.
        """
        self.client.force_login(self.user1)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """
        Tests if the profile view uses the correct template profile.html.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/profile.html')

    def test_register_interface(self):
        """
        Tests if the profile view displays the correct interface to create a profile / student account.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your student profile')
        self.assertContains(response, 'This information cannot be changed later!')
        self.assertContains(response, 'Save profile permanently')

    def test_redirect_for_anonymous_user(self):
        """
        Tests if an anonymous user is redirected to the login page when trying to access the profile view.
        """
        response = self.client.get(reverse('frontend:profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/login/?next=/profile/')










