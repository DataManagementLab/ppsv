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


def topic_selection(request):
    """selection view

    :param request: The given request
    :type request: HttpRequest
    """

    template_name = 'frontend/selection.html'
    all_faculties = models.Course.objects.order_by().values('faculty').distinct()
    args = {}

    # If a form with the method "post" is submitted by a button
    if request.method == "POST":

        # If a button with the name "faculty_button" is pressed in "selection.html"
        if "faculty_button" in request.POST:

            # "chosen_faculty" contains the faculty id of the pressed "faculty_button"
            chosen_faculty = str(request.POST.get('faculty_button'))
            # "courses_in_chosen_faculty" is a QuerySet with all courses in the database
            # which are in the "chosen_faculty"
            chosen_course = models.Course.objects.filter(faculty=chosen_faculty)

            args = {'courses': chosen_course, "faculties": all_faculties}

            return render(request, template_name, args)

        # If a button with the name 'course_button' is pressed in "selection.html"
        elif "course_button" in request.POST:

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
        elif "topic_button" in request.POST:

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

                if request.user.is_authenticated:
                    # "unfiltered_groups_of_student" contains all groups which contain the logged in student
                    unfiltered_groups_of_student = models.Group.objects.filter(students=str(request.user.student))

                    # "groups_of_student" contains all groups which contain the logged in student and fulfil all
                    # conditions (1 < group.size <= chosen.topic.max_participants)
                    groups_of_student = []

                    # delete all groups with size=1 and size >= the allowed max participants of the chosen topic
                    # in order to get the groups which do not only contain the logged in student himself and have the
                    # correct group size
                    for group in unfiltered_groups_of_student:
                        if 1 < group.size <= models.Topic.objects.get(id=chosen_topic).max_participants:
                            groups_of_student.append(group)
                    args["groups_of_student"] = groups_of_student

                args["courses"] = courses_in_same_faculty
                args["topics_in_chosen_course"] = topics_in_chosen_course
                args["chosen_topic"] = chosen_topic
                args["chosen_course"] = chosen_course.id

        elif "select_topic_button" in request.POST:

            # Initialising "success" which will later indicate the selection page if the selection succeeded
            success = ''

            # "student_tu_id" contains the tucan_id of the student who is logged in
            student_tu_id = str(request.user.student)

            # "chosen_topic_id" contains the id of the topic which was selected by the user by pressing the
            # according button on the selection page
            chosen_topic_id = int(request.POST.get('select_topic_button'))

            # "chosen_course" contains the course which contains the chosen topic
            chosen_course = models.Course.objects.get(topic=chosen_topic_id)
            # "courses_in_same_faculty" contains all courses which have the same faculty as the "chosen_course"
            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)
            # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)
            # "group_of_student" contains the group with which the user will select the chosen topic
            group_of_student = "#"

            students_in_group = []
            counter = 0
            while not (request.POST.get("student_added" + str(counter)) is None):
                students_in_group.append(str(request.POST.get("student_added" + str(counter))))
                counter += 1

            if counter >= 1:
                existing_groups = models.Group.objects.filter(students=student_tu_id)
                for student in students_in_group:
                    existing_groups = existing_groups.filter(students=student)

                if len(existing_groups) == 0:
                    print("Does Not Exist")

                    for student_id in students_in_group:
                        students_in_group[students_in_group.index(student_id)] = \
                            models.Student.objects.get(tucan_id=student_id)

                    group_of_student = Group()
                    group_of_student.save()
                    for student in students_in_group:
                        group_of_student.students.add(student)

                    # "topic_selections_of_group" contains all selections made by the "group_of_student" group
                    topic_selections_of_group = models.TopicSelection.objects.filter(group=group_of_student.id)
                    print(topic_selections_of_group)

                    user_selection = TopicSelection()
                    user_selection.priority = 0
                    user_selection.group = group_of_student
                    user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
                    user_selection.save()
                    # "success" indicates the selection page that the selection succeeded
                    success = 'success'

                    # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
                    # be interpreted as "no topic chosen"
                    chosen_topic_id = -1

                else:
                    # "topic_selections_of_group" contains all selections made by the "group_of_student" group
                    topic_selections_of_group = models.TopicSelection.objects.filter(group=existing_groups[0].id)

                    already_selected = False

                    # Iterates through all known selections which the group already made
                    for known_selection in topic_selections_of_group:
                        # If the chosen topic was already selected by the group, the selection "fails"
                        if int(chosen_topic_id) == int(known_selection.topic.id):
                            already_selected = True
                            # "already_selected" indicates the selection page that the chosen topic
                            # was already selected
                            success = 'already_selected'
                            print("Hallo")

                    # If a selection of the chosen topic by the "group_of_student" does not exist,
                    # a selection will be created
                    if not already_selected:
                        user_selection = TopicSelection()
                        user_selection.priority = 0
                        user_selection.group = existing_groups[0]
                        user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
                        user_selection.save()
                        # "success" indicates the selection page that the selection succeeded
                        success = 'success'

                    # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
                    # be interpreted as "no topic chosen"
                    chosen_topic_id = -1

            else:

                data = str(request.POST.get("group_selection")).split("|")

                chosen_group = int(data[0])
                chosen_topic_id = int(data[1])

                # "topic_selections_of_group" contains all selections made by the "group_of_student" group
                topic_selections_of_group = models.TopicSelection.objects.filter(group=chosen_group)

                already_selected = False

                # Iterates through all known selections which the group already made
                for known_selection in topic_selections_of_group:
                    # If the chosen topic was already selected by the group, the selection "fails"
                    if int(chosen_topic_id) == int(known_selection.topic.id):
                        already_selected = True
                        # "already_selected" indicates the selection page that the chosen topic
                        # was already selected
                        success = 'already_selected'
                        print("Hallo")

                # If a selection of the chosen topic by the "group_of_student" does not exist,
                # a selection will be created
                if not already_selected:
                    user_selection = TopicSelection()
                    user_selection.priority = 0
                    user_selection.group = models.Group.objects.get(id=chosen_group)
                    user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
                    user_selection.save()
                    # "success" indicates the selection page that the selection succeeded
                    success = 'success'

                # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
                # be interpreted as "no topic chosen"
                chosen_topic_id = -1

            args["courses"] = courses_in_same_faculty
            args["topics_in_chosen_course"] = topics_in_chosen_course
            args["chosen_topic"] = chosen_topic_id
            args["chosen_course"] = chosen_course.id
            args["success"] = success

        elif "display_text_fields" in request.POST:

            chosen_topic_id = int(request.POST.get('display_text_fields'))

            chosen_course = models.Course.objects.get(topic=chosen_topic_id)

            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

            # "unfiltered_groups_of_student" contains all groups which contain the logged in student
            unfiltered_groups_of_student = models.Group.objects.filter(students=str(request.user.student))

            groups_of_student = []
            # delete all groups with size=1 and size >= the allowed max participants of the chosen topic
            # in order to get the groups which do not only contain the logged in student himself and have the
            # correct group size
            for group in unfiltered_groups_of_student:
                if 1 < group.size <= models.Topic.objects.get(id=chosen_topic_id).max_participants:
                    groups_of_student.append(group)

            open = True

            student_added = [str(request.user.student)]

            student_id = str(request.user.student)

            args["courses"] = courses_in_same_faculty
            args["topics_in_chosen_course"] = topics_in_chosen_course
            args["chosen_course"] = chosen_course.id
            args["chosen_topic"] = chosen_topic_id
            args["open"] = open
            args["student_added"] = student_added
            args["student_id"] = student_id
            args["groups_of_student"] = groups_of_student

        elif "add_student" or "remove_student" or "group_selection" or "without_group" in request.POST:

            chosen_topic_id = None
            chosen_group = None

            if "add_student" in request.POST:
                chosen_topic_id = int(request.POST.get("add_student"))
            if "remove_student" in request.POST:
                chosen_topic_id = int(request.POST.get("topic_id"))
            if "group_selection" in request.POST:
                data = str(request.POST.get("group_selection")).split("|")
                if int(data[0]) != -1:
                    chosen_group = int(data[0])
                    args["chosen_group"] = chosen_group
                chosen_topic_id = int(data[1])
            if "without_group" in request.POST:
                args = select(request)
                return render(request, template_name, args)

            # "unfiltered_groups_of_student" contains all groups which contain the logged in student
            unfiltered_groups_of_student = models.Group.objects.filter(students=str(request.user.student))

            groups_of_student = []
            # delete all groups with size=1 and size >= the allowed max participants of the chosen topic
            # in order to get the groups which do not only contain the logged in student himself and have the
            # correct group size
            for group in unfiltered_groups_of_student:
                if 1 < group.size <= models.Topic.objects.get(id=chosen_topic_id).max_participants:
                    groups_of_student.append(group)

            chosen_course = models.Course.objects.get(topic=chosen_topic_id)

            courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

            student_id = str(request.user.student)

            open = False

            if chosen_group is None:
                if "add_student" or "remove_student" in request.POST:

                    open = True

                    already_added_student = False

                    student_added = []

                    counter = 0

                    while not (request.POST.get("student_added" + str(counter)) is None):
                        student_added.append(str(request.POST.get("student_added" + str(counter))))
                        counter += 1

                    if "add_student" in request.POST:
                        if models.Topic.objects.get(id=chosen_topic_id).max_participants > counter:
                            if "".join(request.POST.get("new_student_id").split()) != "":
                                if "".join(request.POST.get("new_student_id").split()) != str(request.user.student):
                                    if student_added.count(str(request.POST.get("new_student_id"))) == 0:
                                        if models.Student.objects.filter(
                                                tucan_id=request.POST.get("new_student_id")).exists():
                                            student_added.append(str(request.POST.get("new_student_id")))
                                    else:
                                        already_added_student = True

                    if "remove_student" in request.POST:
                        student_added.remove(str(request.POST.get("remove_student")))

                    args["student_added"] = student_added
                    args["already_added_student"] = already_added_student

            args["open"] = open
            args["topics_in_chosen_course"] = topics_in_chosen_course
            args["courses"] = courses_in_same_faculty
            args['chosen_course'] = chosen_course.id
            args["chosen_topic"] = chosen_topic_id
            args["student_id"] = student_id
            args["groups_of_student"] = groups_of_student

    args["faculties"] = all_faculties
    return render(request, template_name, args)


def select(request):
    template_name = 'frontend/selection.html'
    all_faculties = models.Course.objects.order_by().values('faculty').distinct()
    args = {}

    # Initialising "success" which will later indicate the selection page if the selection succeeded
    success = ''

    # "student_tu_id" contains the tucan_id of the student who is logged in
    student_tu_id = str(request.user.student)

    # "chosen_topic_id" contains the id of the topic which was selected by the user by pressing the
    # according button on the selection page
    chosen_topic_id = int(request.POST.get("without_group"))

    # "chosen_course" contains the course which contains the chosen topic
    chosen_course = models.Course.objects.get(topic=chosen_topic_id)
    # "courses_in_same_faculty" contains all courses which have the same faculty as the "chosen_course"
    courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)
    # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
    topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)
    # "group_of_student" contains the group with which the user will select the chosen topic
    group_of_student = ""

    students_in_group = [str(request.user.student)]

    existing_groups = []
    for group in models.Group.objects.filter(students=student_tu_id):
        if group.size == 1:
            existing_groups.append(group)

    if len(existing_groups) == 0:

        group_of_student = Group()
        group_of_student.save()
        group_of_student.students.add(student_tu_id)

        user_selection = TopicSelection()
        user_selection.priority = 0
        user_selection.group = group_of_student
        user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
        user_selection.save()
        # "success" indicates the selection page that the selection succeeded
        success = 'success'

        # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
        # be interpreted as "no topic chosen"
        chosen_topic_id = -1

    else:
        # "topic_selections_of_group" contains all selections made by the "group_of_student" group
        topic_selections_of_group = models.TopicSelection.objects.filter(group=existing_groups[0].id)

        already_selected = False

        # Iterates through all known selections which the group already made
        for known_selection in topic_selections_of_group:
            # If the chosen topic was already selected by the group, the selection "fails"
            if int(chosen_topic_id) == int(known_selection.topic.id):
                already_selected = True
                # "already_selected" indicates the selection page that the chosen topic
                # was already selected
                success = 'already_selected'

        # If a selection of the chosen topic by the "group_of_student" does not exist,
        # a selection will be created
        if not already_selected:
            user_selection = TopicSelection()
            user_selection.priority = 0
            user_selection.group = existing_groups[0]
            user_selection.topic = models.Topic.objects.get(id=chosen_topic_id)
            user_selection.save()
            # "success" indicates the selection page that the selection succeeded
            success = 'success'

        # In order to close the button under the chosen topic, the chosen topic need to be "-1" which will
        # be interpreted as "no topic chosen"
        chosen_topic_id = -1

    args["courses"] = courses_in_same_faculty
    args["topics_in_chosen_course"] = topics_in_chosen_course
    args["chosen_topic"] = chosen_topic_id
    args["chosen_course"] = chosen_course.id
    args["success"] = success
    args["faculties"] = all_faculties

    return args


def overview(request):
    template_name = 'frontend/overview.html'

    if request.user.is_authenticated:

        args = {}

        if hasattr(request.user, "student"):

            student_tucan_id = str(request.user.student)

            groups_of_student = []
            selections_of_groups = []

            if models.Group.objects.filter(students=student_tucan_id).exists():
                groups_of_student = models.Group.objects.filter(students=student_tucan_id)
                for group in groups_of_student:
                    selections_of_groups.append(models.TopicSelection.objects.filter(group=group.id))

            if request.method == "POST":

                if 'set_priority_button' in request.POST:

                    topic_id = str(request.POST.get('topic_id'))
                    priority = int(request.POST.get('priority'))
                    group_id = str(request.POST.get('group_id'))

                    another_topic_has_same_priority = False
                    for selections in selections_of_groups:
                        for selection in selections:
                            if str(selection.group.id) == group_id:
                                if str(selection.topic.pk) != topic_id:
                                    if selection.priority == priority and priority != 0:
                                        messages.error(request, "You can't have two topics with the same priority !")
                                        another_topic_has_same_priority = True
                                        break

                    if not another_topic_has_same_priority:
                        selection = get_selection(selections_of_groups, group_id, topic_id)
                        selection.priority = priority
                        selection.save()

                elif 'remove_topic_button' in request.POST:

                    topic_id = str(request.POST.get('remove_topic_button'))
                    group_id = str(request.POST.get('group_id'))

                    priority_of_removed_topic = get_selection(selections_of_groups, group_id, topic_id).priority

                    get_selection(selections_of_groups, group_id, topic_id).delete()
                    selections_of_groups.clear()
                    if models.Group.objects.filter(students=student_tucan_id).exists():
                        groups_of_student = models.Group.objects.filter(students=student_tucan_id)
                        for group in groups_of_student:
                            selections_of_groups.append(models.TopicSelection.objects.filter(group=group.id))

                    if priority_of_removed_topic != 0:
                        for selections in selections_of_groups:
                            for selection in selections:
                                if str(selection.group.id) == str(group_id):
                                    if int(selection.priority) > int(priority_of_removed_topic):
                                        selection.priority = int(selection.priority) - 1
                                        selection.save()

                elif 'open_motivation_text_button' in request.POST:
                    open_motivation_text_for = int(request.POST.get('open_motivation_text_button'))
                    group_id = int(request.POST.get('group_id'))
                    print(group_id)
                    for selections_of_group in selections_of_groups:
                        for selection in selections_of_group:
                            if selection.id == open_motivation_text_for and selection.group.id == group_id:
                                motivation_text_of_selection = selection.motivation
                                break

                    args["open_motivation_text_for"] = open_motivation_text_for
                    args["motivation_text_of_selection"] = motivation_text_of_selection

                elif 'save_motivation_text_button' in request.POST:
                    save_motivation_text_for = int(request.POST.get('save_motivation_text_button'))
                    group_id = int(request.POST.get('group_id'))
                    motivation_text = str(request.POST.get('motivation_text'))

                    for selections_of_group in selections_of_groups:
                        for selection in selections_of_group:
                            if selection.id == save_motivation_text_for and selection.group.id == group_id:
                                selection.motivation = motivation_text
                                selection.save()
                                messages.success(request, "Your motivation text has been saved.")
                                break

            sorted_selections_of_groups = []
            for selections in selections_of_groups:
                sorted_selections_of_groups.append(sorted(selections, key=lambda x: x.priority))
            selections_of_groups = sorted_selections_of_groups

            motivation_text_needed = []
            for selections in selections_of_groups:
                for selection in selections:
                    course_of_selected_topic = models.Course.objects.get(topic=selection.topic.id)
                    info = []
                    if course_of_selected_topic.motivation_text:
                        info.append((selection, True))
                        motivation_text_needed.append(info)
                    else:
                        info.append((selection, False))
                        motivation_text_needed.append(info)

            args["student_tu_id"] = student_tucan_id
            args["groups_of_student"] = groups_of_student
            args["selections_of_groups"] = selections_of_groups
            args["motivation_text_needed"] = motivation_text_needed

        return render(request, template_name, args)

    return render(request, template_name)


# Help functions of overview
def get_selection(selections_of_groups, group_id, topic_id):
    for selections in selections_of_groups:
        for selection in selections:
            if str(selection.group.pk) == str(group_id):
                if str(selection.topic.pk) == topic_id:
                    return selection


# Help functions of overview

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
