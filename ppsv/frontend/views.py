"""Purpose of this file
This file describes the frontend views.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from course import models
from .forms.forms import NewUserForm, NewStudentForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from course.models import TopicSelection, Group
from django.contrib.auth.models import User


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def overview(request):
    template_name = 'frontend/overview.html'

    args = {}
    if request.method == "POST":

        if "faculty_view" in request.POST:

            all_faculties = models.Course.objects.values("faculty").distinct().order_by("faculty")

            faculties = {}
            for faculty in all_faculties:
                course = models.Course.objects.filter(faculty=faculty["faculty"])
                faculties[faculty.get("faculty")] = course[0].get_faculty_display()

            args["faculties"] = faculties

        elif "choose_faculty" in request.POST:

            chosen_faculty = str(request.POST.get("choose_faculty"))
            courses_in_chosen_faculty = models.Course.objects.filter(faculty=chosen_faculty)

            args["chosen_faculty"] = chosen_faculty
            if len(courses_in_chosen_faculty) != 0:
                args["courses"] = courses_in_chosen_faculty
            else:
                args["courses"] = "No_Courses"

        elif "choose_course" in request.POST:

            data = str(request.POST.get("choose_course")).split("|")
            chosen_course = data[0]
            chosen_faculty = data[1]
            open_course_info = data[2]

            topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course)

            args["chosen_faculty"] = chosen_faculty
            args["chosen_course"] = models.Course.objects.get(id=chosen_course)
            if len(topics_in_chosen_course) != 0:
                args["topics"] = topics_in_chosen_course
            else:
                args["topics"] = "No_Topics"

            if open_course_info == "True":
                args["open_course_info"] = True
            else:
                args["open_course_info"] = False

        elif any(["choose_topic" in request.POST, "open_group_select" in request.POST,
                  "select_topic" in request.POST, "select_with_chosen_group" in request.POST,
                  "open_group_create" in request.POST, "add_student" in request.POST,
                  "remove_student" in request.POST, "select_with_new_group" in request.POST]):

            if "choose_topic" in request.POST:
                data = str(request.POST.get("choose_topic")).split("|")
            if request.user.is_authenticated and hasattr(request.user, "student"):
                if "open_group_select" in request.POST:
                    data = str(request.POST.get("open_group_select")).split("|")
                    args["open_group_select"] = True
                    args["groups"] = filter(lambda x: 1 < x.size <= models.Topic.objects.get(id=data[0]).max_participants,
                                            models.Group.objects.filter(students=request.user.student))
                elif "select_topic" in request.POST:
                    data = str(request.POST.get("select_topic")).split("|")
                    student_tu_id = str(request.user.student)

                    selected_topic_id = int(data[0])

                    existing_groups = []
                    for group in models.Group.objects.filter(students=student_tu_id):
                        if group.size == 1:
                            existing_groups.append(group)

                    if len(existing_groups) == 0:

                        group_of_student = Group()
                        group_of_student.save()
                        group_of_student.students.add(student_tu_id)

                        user_selection = TopicSelection()
                        user_selection.priority = 1
                        user_selection.group = group_of_student
                        user_selection.topic = models.Topic.objects.get(id=selected_topic_id)
                        user_selection.save()

                        messages.success(request,
                                         "Your Selection Was Successful! "
                                         "You can find and edit your chosen topics on the "
                                         "\"Your Selection\" page.")

                        messages.warning(request,
                                         "You need to add a motivation text(when required) "
                                         "to your selection in order to fully "
                                         "complete your selection. You can do this on the \"Your Selection\" page.")

                    else:

                        topic_selections_of_group = models.TopicSelection.objects.filter(group=existing_groups[0].id)

                        already_selected = False

                        for known_selection in topic_selections_of_group:
                            if int(selected_topic_id) == int(known_selection.topic.id):
                                already_selected = True
                                messages.error(request, "Selection Failed! You have already selected this topic.")

                        if not already_selected:
                            user_selection = TopicSelection()
                            user_selection.priority = len(topic_selections_of_group) + 1
                            user_selection.group = existing_groups[0]
                            user_selection.topic = models.Topic.objects.get(id=selected_topic_id)
                            user_selection.save()
                            messages.success(request,
                                             "Your Selection Was Successful! You can find and edit your chosen topics on the "
                                             "\"Your Selection\" page.")

                            messages.warning(request,
                                             "You need to add a motivation text(when required) "
                                             "to your selection in order to fully "
                                             "complete your selection. You can do this on the \"Your Selection\" page.")
                elif "select_with_chosen_group" in request.POST:
                    data = str(request.POST.get("select_with_chosen_group")).split("|")
                    selected_topic_id = data[0]
                    chosen_group_id = str(request.POST.get("group_options"))
                    topic_selections_of_group = models.TopicSelection.objects.filter(group=chosen_group_id)
                    already_selected = False
                    for known_selection in topic_selections_of_group:
                        if int(selected_topic_id) == int(known_selection.topic.id):
                            already_selected = True
                            messages.error(request, "Selection Failed! You have already selected this topic.")

                    if not already_selected:
                        selection = TopicSelection()
                        selection.priority = len(topic_selections_of_group) + 1
                        selection.group = models.Group.objects.get(id=chosen_group_id)
                        selection.topic = models.Topic.objects.get(id=selected_topic_id)
                        selection.save()

                        messages.success(request,
                                         "Your Selection Was Successful!"
                                         " You can find and edit your chosen topics on the your selection page.")
                        messages.warning(request,
                                         "You need to add a motivation text(when required) "
                                         "to your selection in order to fully complete your selection. "
                                         "You can do this on the your selection page.")
                elif "open_group_create" in request.POST:
                    data = str(request.POST.get("open_group_create")).split("|")
                    args["members_in_new_group"] = [request.user.student.tucan_id]
                    args["open_group_create"] = True
                elif "add_student" in request.POST:
                    data = str(request.POST.get("add_student")).split("|")

                    members_in_new_group = []
                    counter = 0
                    while not (request.POST.get("member" + str(counter)) is None):
                        members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                        counter += 1

                    if "".join(request.POST.get("new_student_id").split()) != "":
                        if members_in_new_group.count(str(request.POST.get("new_student_id"))) == 0:
                            if models.Topic.objects.get(id=data[0]).max_participants > counter:
                                if models.Student.objects.filter(
                                        tucan_id=request.POST.get("new_student_id")).exists():
                                    members_in_new_group.insert(0, str(request.POST.get("new_student_id")))
                                else:
                                    messages.error(request, "A student with the tucan id " +
                                                   request.POST.get("new_student_id") +
                                                   " not found.")
                            else:
                                messages.error(request, "Your group would be too large for " +
                                               str(models.Topic.objects.get(id=data[0]).title)
                                               + ". Your group can only have a maximum member count of " +
                                               str(models.Topic.objects.get(id=data[0]).max_participants)
                                               + ".")
                        else:
                            messages.error(request, "A student with the tucan id " +
                                           request.POST.get("new_student_id") +
                                           " is already in the group.")

                    args["members_in_new_group"] = members_in_new_group
                    args["open_group_create"] = True
                elif "remove_student" in request.POST:
                    data = str(request.POST.get("remove_student")).split("|")

                    members_in_new_group = []
                    counter = 0
                    while not (request.POST.get("member" + str(counter)) is None):
                        members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                        counter += 1

                    members_in_new_group.remove(data[4])

                    args["members_in_new_group"] = members_in_new_group
                    args["open_group_create"] = True
                elif "select_with_new_group" in request.POST:
                    data = str(request.POST.get("select_with_new_group")).split("|")

                    members_in_new_group = []
                    counter = 0
                    while not (request.POST.get("member" + str(counter)) is None):
                        members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                        counter += 1

                    existing_groups = []
                    for member in members_in_new_group:
                        if models.Group.objects.filter(students=member).exists():
                            existing_groups.append(models.Group.objects.filter(students=member))

                    exception = False

                    if len(members_in_new_group) == 1:
                        messages.error(request, f"Your group needs to contain more members than yourself !")
                        exception = True

                    for groups_of_member in existing_groups:
                        if not exception:
                            for group in groups_of_member:
                                if set(members_in_new_group).issubset(
                                        "".join(group.get_display.split(",")).split()) and len(members_in_new_group) == len(
                                        "".join(group.get_display.split(",")).split()):
                                    messages.error(request, f"This group already exists !")
                                    exception = True
                                    break

                    if not exception:
                        group = Group()
                        group.save()

                        counter = 0
                        while not (request.POST.get("member" + str(counter)) is None):
                            group.students.add(
                                models.Student.objects.get(tucan_id=request.POST.get("member" + str(counter))))
                            counter += 1

                        selection = TopicSelection()
                        selection.group = group
                        selection.topic = models.Topic.objects.get(id=data[0])
                        selection.priority = 1
                        selection.save()

                        messages.success(request,
                                         "Your Selection Was Successful! You can find and edit your chosen topics on the "
                                         "overview page.")
                        messages.warning(request,
                                         "You need to set the priority and add a motivation text(when required) "
                                         "to your selection in order to fully complete your selection. "
                                         "You can do this on the overview page.")

            chosen_topic = data[0]
            chosen_course = data[1]
            chosen_faculty = data[2]
            open_course_info = data[3]

            args["topics"] = [models.Topic.objects.get(id=chosen_topic)]
            args["chosen_faculty"] = chosen_faculty
            args["chosen_course"] = models.Course.objects.get(id=chosen_course)
            args["chosen_topic"] = models.Topic.objects.get(id=chosen_topic)
            if open_course_info == "True":
                args["open_course_info"] = True
            else:
                args["open_course_info"] = False

            if request.user.is_authenticated and hasattr(request.user, "student"):
                all_groups_of_student = models.Group.objects.filter(students=request.user.student)
                all_topics_selected_by_groups = []
                for group in all_groups_of_student:
                    for selection in models.TopicSelection.objects.filter(group=group):
                        all_topics_selected_by_groups.append(selection.topic.id)

                args["selected_topics"] = all_topics_selected_by_groups

    else:

        all_faculties = models.Course.objects.values("faculty").distinct().order_by("faculty")

        faculties = {}
        for faculty in all_faculties:
            course = models.Course.objects.filter(faculty=faculty["faculty"])
            faculties[faculty.get("faculty")] = course[0].get_faculty_display()

        args["faculties"] = faculties

    return render(request, template_name, args)


def your_selection(request):
    template_name = 'frontend/your_selection.html'

    # If the user is logged in and has the attribute "student" the your selection page is loaded
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

                if "remove_topic_button" in request.POST:

                    selection_id = str(request.POST.get('remove_topic_button'))
                    group_id = get_selection(selections_of_groups, selection_id).group.id

                    priority_of_removed_topic = get_selection(selections_of_groups, selection_id).priority

                    get_selection(selections_of_groups, selection_id).delete()
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

                elif "edit_motivation_text_button" in request.POST:
                    open_motivation_text_for_selection = int(request.POST.get("edit_motivation_text_button"))

                    for selections_of_group in selections_of_groups:
                        for selection in selections_of_group:
                            if selection.id == open_motivation_text_for_selection:
                                motivation_text_of_selection = selection.motivation
                                break

                    args["open_motivation_text_for_selection"] = open_motivation_text_for_selection
                    args["motivation_text_of_selection"] = motivation_text_of_selection

                elif "save_motivation_text_button" in request.POST:
                    save_motivation_text_for = int(request.POST.get("save_motivation_text_button"))
                    motivation_text = str(request.POST.get("motivation_text"))

                    for selections_of_group in selections_of_groups:
                        for selection in selections_of_group:
                            if selection.id == save_motivation_text_for:
                                selection.motivation = motivation_text
                                selection.save()
                                messages.success(request, "Your motivation text has been saved.")
                                break

                elif "up_priority" in request.POST:
                    chosen_selection_id = int(request.POST.get("up_priority"))
                    chosen_selection = get_selection(selections_of_groups, chosen_selection_id)

                    for selections in selections_of_groups:
                        for selection in selections:
                            if selection.group.pk == chosen_selection.group.pk and selection.pk != chosen_selection.pk:
                                if selection.priority == chosen_selection.priority - 1:
                                    selection.priority = chosen_selection.priority
                                    selection.save()
                                    chosen_selection.priority = chosen_selection.priority - 1
                                    chosen_selection.save()
                                    break

                elif "down_priority" in request.POST:
                    chosen_selection_id = int(request.POST.get("down_priority"))
                    chosen_selection = get_selection(selections_of_groups, chosen_selection_id)

                    for selections in selections_of_groups:
                        for selection in selections:
                            if selection.group.pk == chosen_selection.group.pk and selection.pk != chosen_selection.pk:
                                if selection.priority == chosen_selection.priority + 1:
                                    selection.priority = chosen_selection.priority
                                    selection.save()
                                    chosen_selection.priority = chosen_selection.priority + 1
                                    chosen_selection.save()
                                    break

            sorted_selections_of_groups = []
            for selections in selections_of_groups:
                sorted_selections_of_groups.append(sorted(selections, key=lambda x: x.priority))
            selections_of_groups = sorted_selections_of_groups

            motivation_text_required = []
            for selections in selections_of_groups:
                for selection in selections:
                    course_of_selected_topic = models.Course.objects.get(topic=selection.topic.id)
                    info = []
                    if course_of_selected_topic.motivation_text:
                        info.append((selection, True))
                        motivation_text_required.append(info)
                    else:
                        info.append((selection, False))
                        motivation_text_required.append(info)

            if 'save_motivation_text_button' not in request.POST and not request.POST.get(
                    "open_motivation_text_for_selection") is None:
                open_motivation_text_for_selection = int(request.POST.get("open_motivation_text_for_selection"))

                for selections_of_group in selections_of_groups:
                    for selection in selections_of_group:
                        if selection.id == open_motivation_text_for_selection:
                            motivation_text_of_selection = selection.motivation
                            break

                args["open_motivation_text_for_selection"] = open_motivation_text_for_selection
                args["motivation_text_of_selection"] = motivation_text_of_selection

            if not request.POST.get("open_selection_info") is None:
                info_selection = models.TopicSelection.objects.get(id=int(request.POST.get("open_selection_info")))
                args["info_selection"] = info_selection
                if str(request.POST.get("open_course_info")) == 'True':
                    args["open_course_info"] = True
                else:
                    args["open_course_info"] = False

            args["student_tu_id"] = student_tucan_id
            args["groups_of_student"] = groups_of_student
            args["selections_of_groups"] = selections_of_groups
            args["motivation_text_required"] = motivation_text_required

            if "info_button" in request.POST:
                info_selection = models.TopicSelection.objects.get(id=int(request.POST.get("info_button")))
                open_course_info = False

                args["info_selection"] = info_selection
                args["open_course_info"] = open_course_info

            if "course_info_button" in request.POST:

                open = "".join(str(request.POST.get("selection")).split("|")[0].split())
                if open == "False":
                    info_selection = models.TopicSelection.objects.get(
                        id=int(str(request.POST.get("selection")).split("|")[1]))
                    open_course_info = True
                else:
                    info_selection = models.TopicSelection.objects.get(
                        id=int(str(request.POST.get("selection")).split("|")[1]))
                    open_course_info = False

                args["info_selection"] = info_selection
                args["open_course_info"] = open_course_info

        return render(request, template_name, args)

    return render(request, template_name)


# Help functions of your_selection
def get_selection(selections_of_groups, chosen_selection_id):
    for selections in selections_of_groups:
        for selection in selections:
            if int(selection.id) == int(chosen_selection_id):
                return selection


def groups(request):
    template_name = 'frontend/groups.html'

    if request.user.is_authenticated:

        args = {}

        if hasattr(request.user, "student"):

            groups_of_student = models.Group.objects.filter(students=request.user.student.tucan_id)
            members_of_groups = {}
            for group in groups_of_student:
                members = []
                for tucan_id in "".join(group.get_display.split(",")).split():
                    members.append(User.objects.get(student=tucan_id))
                members_of_groups[group.id] = members

            args["groups_of_student"] = groups_of_student
            args["members_of_groups"] = members_of_groups

            if request.method == "POST":

                if "ask_delete_group" in request.POST:
                    chosen_group = int(request.POST.get("ask_delete_group"))
                    args["chosen_group"] = chosen_group
                elif "delete_group" in request.POST:
                    models.Group.objects.get(id=int(request.POST.get("delete_group"))).delete()

    return render(request, template_name, args)


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
            messages.success(request, "Student profile saved successfully.")
            return redirect("frontend:homepage")
        if hasattr(request.user, "student"):
            # maybe overwriting the current student is possible, but changing the primary key is troublesome
            messages.error(request, "Student profile could not be saved. A user can only create one student.")
        else:
            messages.error(request, "Saving unsuccessful. Invalid information.")
    form = NewStudentForm()
    return render(request=request, template_name="registration/profile.html", context={"profile_form": form})
