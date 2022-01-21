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
from django.db.models import Sum


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def selection(request):
    """selection view

    :param request: The given request
    :type request: HttpRequest
    """

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
            chosen_course = models.Course.objects.filter(faculty=chosen_faculty)

            args = {'courses': chosen_course, "faculties": all_faculties}

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
                chosen_course = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=course_id).faculty)

                args = {'courses': chosen_course, "faculties": all_faculties}

                return render(request, template_name, args)

            # If the "course_button" is clicked the first time, we need to get all topics in thr chosen course
            else:
                # In order to still display all courses in the same faculty after we closed the overview for the
                # topics, we need to get all courses in the chosen faculty again
                courses_in_same_faculty = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=chosen_course).faculty)
                # "topics_in_chosen_course" contains all topics in the chosen course
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course)

                args = {"courses": courses_in_same_faculty, 'chosen_course': chosen_course,
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

                # "groups_of_student" contains all groups which contain the logged in student
                groups_of_student = models.Group.objects.filter(students=str(request.user.student))

                # delete all groups with size=1 in order to get the groups
                # which do not only contain the logged in student himself
                for group in groups_of_student:
                    if group.size == 1:
                        groups_of_student.get(id=group.id).delete()

                args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                        "faculties": all_faculties, "chosen_topic": chosen_topic,
                        'chosen_course': chosen_course.id, 'groups_of_student': groups_of_student}

                return render(request, template_name, args)

        elif 'select_topic_button' in request.POST:

            # Initialising "success" which will later indicate the selection page if the selection succeeded
            success = ''

            # "student_tu_id" contains the tucan_id of the student who is logged in
            student_tu_id = str(request.user.student)

            # "chosen_topic_id" contains the id of the topic which was selected by the user by pressing the
            # according button on the selection page
            chosen_topic_id = int(request.POST.get('select_topic_button'))

            students_in_group = []
            counter = 1;
            while not (request.POST.get("student_added" + str(counter)) is None):
                students_in_group.append(str(request.POST.get("student_added" + str(counter))))
                counter += 1

            students_in_group.append(student_tu_id)

            for student_id in students_in_group:
                if not models.Student.objects.filter(tucan_id=student_id).exists():
                    success = "student_does_not_exist"
                else:
                    students_in_group[students_in_group.index(student_id)] = \
                        models.Student.objects.get(tucan_id=student_id)

            print(students_in_group)

            print(models.Group.objects.filter(students=student_tu_id))

            if success == "":
                created_group = Group()
                created_group.save()
                for student in students_in_group:
                    created_group.students.add(student)
                # If a group for the student (with him as the only group member) does not exist, it will be created
                if not models.Group.objects.filter(students=student_tu_id).exists():
                    created_group.save()

            # "group_of_student" contains the group with which the user will select the chosen topic
            group_of_student = models.Group.objects.get(students=student_tu_id)

            # "topic_selections_of_group" contains all selections made by the "group_of_student" group
            topic_selections_of_group = models.TopicSelection.objects.filter(group=group_of_student.id)

            already_selected = False

            # Iterates through all known selections which the group already made
            for known_selection in topic_selections_of_group:
                # If the chosen topic was already selected by the group, the selection "fails"
                if int(chosen_topic_id) == int(known_selection.topic.id):
                    already_selected = True
                    # "already_selected" indicates the selection page that the chosen topic
                    # was already selected
                    success = 'already_selected'

            # If a selection of the chosen topic by the "group_of_student" does not exist, a selection will be created
            if not already_selected:
                user_selection = TopicSelection()
                user_selection.priority = 0
                user_selection.group = group_of_student
                user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
                user_selection.save()
                # "success" indicates the selection page that the selection succeeded
                success = 'success'

            # "chosen_course" contains the course which contains the chosen topic
            chosen_course = models.Course.objects.get(topic=chosen_topic_id)
            # "courses_in_same_faculty" contains all courses which have the same faculty as the "chosen_course"
            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)
            # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

            # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
            # be interpreted as "no topic chosen"
            chosen_topic_id = -1

            args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                    "faculties": all_faculties,
                    "chosen_topic": chosen_topic_id, 'chosen_course': chosen_course.id, 'success': success}
            return render(request, template_name, args)

        elif "display_text_fields" in request.POST:

            chosen_topic_id = int(request.POST.get('display_text_fields'))

            chosen_course = models.Course.objects.get(topic=chosen_topic_id)

            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

            open = True

            args = {"faculties": all_faculties, "courses": courses_in_same_faculty,
                    "topics_in_chosen_course": topics_in_chosen_course, 'chosen_course': chosen_course.id,
                    "chosen_topic": chosen_topic_id, "open": open}
            return render(request, template_name, args)

        elif "add_student" or "remove_student" in request.POST:

            chosen_topic_id = ""
            if "add_student" in request.POST:
                chosen_topic_id = int(request.POST.get('add_student'))
            else :
                chosen_topic_id = int(request.POST.get('topic_id'))

            chosen_course = models.Course.objects.get(topic=chosen_topic_id)

            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

            open = True
            already_added_student = False

            student_added = []
            if request.POST.get("new_student_id") != "":
                student_added.append(str(request.POST.get("new_student_id")))

            counter = 1;
            while not (request.POST.get("student_added" + str(counter)) is None):
                student_added.append(str(request.POST.get("student_added" + str(counter))))
                counter += 1

            if student_added.count(str(request.POST.get("new_student_id"))) > 1:
                student_added.remove(str(request.POST.get("new_student_id")))
                already_added_student = True

            if "remove_student" in request.POST:
                student_added.remove(str(request.POST.get("remove_student")))

            args = {"faculties": all_faculties, "courses": courses_in_same_faculty,
                    "topics_in_chosen_course": topics_in_chosen_course, 'chosen_course': chosen_course.id,
                    "chosen_topic": chosen_topic_id, "open": open, "student_added": student_added,
                    "already_added_student": already_added_student}
            return render(request, template_name, args)

    args = {"faculties": all_faculties}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'

    if request.user.is_authenticated:

        student_tu_id = str(request.user.student)

        group_of_student = ""
        selections_of_group = ""

        if models.Group.objects.filter(students=student_tu_id).exists():
            group_of_student = models.Group.objects.get(students=student_tu_id)
            selections_of_group = models.TopicSelection.objects.filter(group=group_of_student)

        success = "no_same_priority"

        if request.method == "POST":

            if 'set_priority_button' in request.POST:
                topic_id = str(request.POST.get('topic_id'))
                priority = int(request.POST.get('priority'))

                for selection in selections_of_group:
                    if str(selection.topic) != topic_id:
                        if selection.priority == priority and priority != 0:
                            success = "same_priority"
                            break

                if success == "no_same_priority":
                    for selection in selections_of_group:
                        if str(selection.topic) == topic_id:
                            selection = models.TopicSelection.objects.get(id=selection.id)
                            selection.priority = priority
                            selection.save()

                selections_of_group = models.TopicSelection.objects.filter(group=group_of_student)

            elif 'remove_topic_button' in request.POST:
                topic_id = int(request.POST.get('remove_topic_button'))
                priority = selections_of_group.get(topic=topic_id).priority
                models.TopicSelection.objects.get(group=group_of_student, topic=topic_id).delete()

                selections_of_group = models.TopicSelection.objects.filter(group=group_of_student)
                if not priority == 0:
                    for selection in selections_of_group:
                        if int(selection.priority) > priority:
                            selection.priority = int(selection.priority) - 1
                            selection.save()
                    selections_of_group = models.TopicSelection.objects.filter(group=group_of_student)

        selections_of_group = sorted(selections_of_group, key=lambda x: x.priority)

        motivation_text_needed = []
        for selection in selections_of_group:
            course_of_selected_topic = models.Course.objects.get(topic=selection.topic.id)
            if course_of_selected_topic.motivation_text:
                motivation_text_needed.append((selection, True))
            else:
                motivation_text_needed.append((selection, False))

        args = {"student_tu_id": student_tu_id, "group_of_student": group_of_student,
                "selections_of_group": selections_of_group, "success": success,
                "motivation_text_needed": motivation_text_needed}

        if 'open_motivation_text_button' in request.POST:
            open_motivation_text_for = int(request.POST.get('open_motivation_text_button'))
            print(selections_of_group)
            motivation_text_of_selection = next(filter(lambda x: x.id == open_motivation_text_for,
                                                       selections_of_group)).motivation
            args["open_motivation_text_for"] = open_motivation_text_for
            args["motivation_text_of_selection"] = motivation_text_of_selection

        elif 'save_motivation_text_button' in request.POST:
            save_motivation_text_for = int(request.POST.get('save_motivation_text_button'))
            motivation_text = request.POST.get('motivation_text')
            selection = next(filter(lambda x: x.id == save_motivation_text_for,
                                    selections_of_group))
            selection.motivation = motivation_text
            selection.save()
            args["success"] = "motivational_text_saved"

        return render(request, template_name, args)

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
