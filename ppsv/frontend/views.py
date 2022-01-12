"""Purpose of this file
This file describes the frontend views.
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from course import models
from .forms.forms import NewUserForm, NewStudentForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView
from course.models import TopicSelection, Group


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def selection(request):

    template_name = 'frontend/selection.html'
    all_faculties = models.Course.objects.order_by().values('faculty').distinct()

    # If a form with the method "post" is submitted by a button
    if request.method == "POST":

        # If a button with the name "faculty_button" is pressed in "selection.html"
        if 'faculty_button' in request.POST:

            # "chosen_faculty" contains the faculty id of the pressed "faculty_button"
            chosen_faculty = str(request.POST.get('faculty_button'))
            # "courses_in_chosen_faculty" is a QuerySet with all courses in the database
            # which are in the "chosen_faculty"
            courses_in_chosen_faculty = models.Course.objects.filter(faculty=chosen_faculty)

            args = {'courses': courses_in_chosen_faculty, "faculties": all_faculties}

            return render(request, template_name, args)

        # If a button with the name 'course_button' is pressed in "selection.html"
        elif 'course_button' in request.POST:

            # "chosen_course" contains the course id of the pressed "course_button"
            chosen_course = int(request.POST.get('course_button'))

            # If the value of "chosen_course" is -1, it means that the same button was already clicked
            # one request before. When the button is clicked the first time it opens an overview of
            # the topics which are in "chosen_course" So when the button is clicked a second time
            # it will close the overview. In order to close the overview, "chosen_course" must not be returned
            # with any value.
            if chosen_course == -1:
                # Because the value of "course_button" is now "-1" and not the actual course id,
                # we need to get the course id from an element named "hidden_course_id"
                course_id = int(request.POST.get('hidden_course_id'))

                # In order to still display all courses in the same faculty after we closed the overview for the
                # topics, we need to get all courses in the chosen faculty again
                courses_in_chosen_faculty = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=course_id).faculty)

                args = {'courses': courses_in_chosen_faculty, "faculties": all_faculties}

                return render(request, template_name, args)

            # If the "course_button" is clicked the first time, we need to get all topics in thr chosen course
            else:
                # In order to still display all courses in the same faculty after we closed the overview for the
                # topics, we need to get all courses in the chosen faculty again
                courses_in_chosen_faculty = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=chosen_course).faculty)
                # "topic_choice_set" contains all topics in the chosen course
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course)

                args = {"courses": courses_in_chosen_faculty, 'chosen_course': chosen_course,
                        "topics_in_chosen_course": topics_in_chosen_course, "faculties": all_faculties}

                return render(request, template_name, args)

        # If a button with the name 'topic_button' is pressed in "selection.html"
        elif 'topic_button' in request.POST:

            # "chosen_topic" contains the topic id of the pressed "topic_button"
            chosen_topic = int(request.POST.get('topic_button'))

            # If the value of "chosen_topic" is -1, it means that the same button was already clicked
            # one request before. When the button is clicked the first time it opens a form to select the
            # chosen topic. So when the button is clicked a second time it will close the form.
            # In order to close the form, "chosen_topic" must not be returned with any value.
            if chosen_topic == -1:

                # Because the value of "topic_button" is now "-1" and not the actual topic id,
                # we need to get the topic id from an element named "hidden_topic_id"
                topic_id = int(request.POST.get('hidden_topic_id'))

                # "chosen_course" contains the course which contains the chosen topic
                chosen_course = models.Course.objects.get(topic=topic_id)

                # "course_of_chosen_topic" contains all courses which have the same faculty as the "chosen_course"
                courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

                # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

                args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                        "faculties": all_faculties, 'chosen_course': chosen_course.id}

                return render(request, template_name, args)

            # If the "topic_button" is clicked the first time
            else:

                # "chosen_course" contains the course which contains the chosen topic
                chosen_course = models.Course.objects.get(topic=chosen_topic)

                # "course_of_chosen_topic" contains all courses which have the same faculty as the "chosen_course"
                courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

                # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

                args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                        "faculties": all_faculties, "chosen_topic": chosen_topic,
                        'chosen_course': chosen_course.id}

                return render(request, template_name, args)

        elif 'select_topic_button' in request.POST:

            # Hier sind keine Kommentare weil der Code sich nach dem Merg ändern wird

            # change abcd to logged in student
            student_group = models.Group.objects.get(students='abcd')

            if not student_group:
                print("Empty")
                """
                # Creating a group for the student
                created_group = Group()
                # Change abds to user Tu-ID
                created_group.students.set(models.Student.objects.get(tucan_id='abcd'))
                created_group.save()
                """

            # change abcd to logged in student
            student_group = models.Group.objects.get(students='abcd')
            selections_with_group = models.TopicSelection.objects.filter(group=student_group.id)
            chosen_topic = int(request.POST.get('select_topic_button'))
            success = ''

            already_selected = False
            for known_selection in selections_with_group:
                if int(chosen_topic) == int(known_selection.topic.id):
                        already_selected = True
                        success = 'already_selected'

            if not already_selected:
                # create Group with students in inputtext
                user_selection = TopicSelection()
                user_selection.priority = 0
                # change abcd to logged in student
                user_selection.group = models.Group.objects.get(students='abcd')
                user_selection.topic = models.Topic.objects.get(id=chosen_topic)
                user_selection.save()
                success = 'success'

            courses_in_chosen_faculty = models.Course.objects.filter(topic=chosen_topic)
            courses_in_same_faculty = models.Course.objects.filter(faculty=courses_in_chosen_faculty[0].faculty)
            topics_in_chosen_course = models.Topic.objects.filter(course=courses_in_chosen_faculty[0].id)

            chosen_topic = -1

            args = {'courses': courses_in_same_faculty, "topic_in_chosen_course": topics_in_chosen_course, "faculties": all_faculties,
                    "chosen_topic": chosen_topic, 'chosen_course': courses_in_chosen_faculty[0].id, 'success': success}
            """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                and faculties(contains all faculties)"""
            return render(request, template_name, args)

    args = {"faculties": all_faculties}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'
    return render(request, template_name)


def groups(request):
    template_name = 'frontend/groups.html'
    return render(request, template_name)


def login_request(request):
    """Login view

    :param request: The given request
    :type request: HttpRequest
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        # checks if the given login data is valid
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # proceeds to login the authenticated user
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("frontend:homepage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})


def logout_request(request):
    """Logout view

    :param request: The given request
    :type request: HttpRequest
    """
    # logs the user out
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("frontend:homepage")


def register(request):
    """View for user registration

    :param request: The given request
    :type request: HttpRequest
    """
    if request.method == "POST":
        form = NewUserForm(request.POST)
        # checks if the given data is valid
        if form.is_valid():
            # saves the given data as a new user and the user is logged in
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("frontend:profile")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


@login_required
def profile(request):
    """View for profile/student creation

    :param request: The given request
    :type request: HttpRequest
    """
    if request.method == "POST":
        form = NewStudentForm(request.POST)
        # checks if the given data is valid and the user already has a linked student
        if form.is_valid() and not hasattr(request.user, "student"):
            # saves given data as the new student linked to the user who is logged in
            student = form.save(commit=False)
            student.user = request.user
            student.email = request.user.email
            student.save()
            messages.success(request, "Student creation successful.")
            return redirect("frontend:homepage")
        if hasattr(request.user, "student"):
            messages.error(request, "Student creation unsuccessful. A user can only create one student.")
        else:
            messages.error(request, "Student creation unsuccessful. Invalid information.")
    form = NewStudentForm()
    return render(request=request, template_name="registration/profile.html", context={"profile_form": form})
