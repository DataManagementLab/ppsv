"""Purpose of this file
This file describes the frontend views.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from course import models
from .forms.forms import NewUserForm, NewStudentForm, UserLoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from course.models import TopicSelection, Group
from django.contrib.auth.models import User
from frontend.decorators import user_passes_test
from django.utils.translation import gettext_lazy as _


def homepage(request):
    """View for homepage
    :param request: The given request
    :return: HttpRequest
    """
    template_name = 'frontend/homepage.html'

    if request.user.is_authenticated:
        if hasattr(request.user, "student"):
            # In order to pin messages on the "What to do next" board, one needs to add the message
            # as a key to "recommendations" and the link as the value
            args = {}
            recommendations = {}

            groups_of_student = models.Group.objects.filter(students=request.user.student)
            selections_exist = False
            selections_need_motivation = False
            need_to_assign_topics_to_collection = False
            for group in groups_of_student:
                if models.TopicSelection.objects.filter(group=group).exists():
                    selections_exist = True
                    break

            for group in groups_of_student:
                if models.TopicSelection.objects.filter(group=group, motivation="").exists():
                    for selection in models.TopicSelection.objects.filter(group=group, motivation=""):
                        if selection.topic.course.motivation_text:
                            selections_need_motivation = True
                            break

            for group in groups_of_student:
                if models.TopicSelection.objects.filter(group=group, collection_number=0).exists():
                    need_to_assign_topics_to_collection = True
                    break

            # Pins message to board if motivation texts are missing for selections
            if need_to_assign_topics_to_collection:
                msg = "You still need to assign at least one topic to a collection"
                link = "frontend:your_selection"
                recommendations[msg] = link

            # Pins message to board if motivation texts are missing for selections
            if selections_need_motivation:
                msg = "You still need to write one or more motivation texts"
                link = "frontend:your_selection"
                recommendations[msg] = link

            # Pins message to board if no selections were made
            if not selections_exist:
                msg = "You have not selected any topics yet"
                link = "frontend:overview"
                recommendations[msg] = link
            # Otherwise show where they can be managed
            else:
                msg = "You can view and manage your selected topics here"
                link = "frontend:your_selection"
                recommendations[msg] = link

            # Pins message to board if no group was created
            if len(models.Group.objects.filter(students=request.user.student)) <= 1:
                msg = "You can create a group here"
                link = "frontend:groups"
                recommendations[msg] = link

            args["recommendations"] = recommendations
            return render(request, template_name, args)
        else:
            return render(request, template_name)

    else:
        return login_request(request, template_name)


def overview(request):
    """View for overview page

    :param request: The given request
    :return: HttpRequest
    """
    template_name = 'frontend/overview.html'

    args = {}
    if request.method == "POST":
        # Display all faculties when coming back from somewhere else in overview
        if "faculty_view" in request.POST:

            all_faculties = models.Course.objects.values("faculty").distinct().order_by("faculty")

            faculties = {}
            for faculty in all_faculties:
                course = models.Course.objects.filter(faculty=faculty["faculty"])
                faculties[faculty.get("faculty")] = course[0].get_faculty_display()

            args["faculties"] = faculties
        # when a faculty is chosen show its courses
        elif "choose_faculty" in request.POST:

            chosen_faculty = str(request.POST.get("choose_faculty"))
            courses_in_chosen_faculty = models.Course.objects.filter(faculty=chosen_faculty)

            args["chosen_faculty"] = chosen_faculty
            if len(courses_in_chosen_faculty) != 0:
                available = False
                for course in courses_in_chosen_faculty:
                    if course.get_status in ["Imminent", "Open"]:
                        available = True
                        break
                if available:
                    args["courses"] = courses_in_chosen_faculty
                else:
                    args["courses"] = "No_Courses"
        # when a course is chosen display its topics
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

            if len(topics_in_chosen_course) != 0:
                # Make sure that only authenticated users with a student profile can select topics
                if request.user.is_authenticated and hasattr(request.user, "student"):
                    student_id_of_user = str(request.user.student)

                    show_select_all_topics_button = False
                    for group in models.Group.objects.filter(students=student_id_of_user):
                        topic_selections_of_group = models.TopicSelection.objects.filter(group=group.id)
                        for selected_topic_of_group in topic_selections_of_group:
                            if topics_in_chosen_course.filter(id=selected_topic_of_group.topic.id).exists():
                                show_select_all_topics_button = True
                                break
                        else:
                            continue
                        break
                    args["show_select_remaining_topics_button"] = show_select_all_topics_button
                else:
                    args["show_select_remaining_topics_button"] = False
            else:
                args["show_select_remaining_topics_button"] = False

        # when selecting all remaining topics of a course (alone)
        elif "select_all_remaining_topics" in request.POST:
            data = str(request.POST.get("select_all_remaining_topics")).split("|")
            chosen_course = data[0]
            chosen_faculty = data[1]
            open_course_info = data[2]

            student_id_of_user = str(request.user.student)

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

            group_to_select = None
            for group in models.Group.objects.filter(students=student_id_of_user):
                topic_selections_of_group = models.TopicSelection.objects.filter(group=group.id)
                for selected_topic_of_group in topic_selections_of_group:
                    if topics_in_chosen_course.filter(id=selected_topic_of_group.topic.id).exists():
                        group_to_select = group
                        break
                else:
                    continue
                break

            if group_to_select is not None:
                topic_selections_of_group = models.TopicSelection.objects.filter(group=group_to_select.id)
                for topic_to_select in topics_in_chosen_course:
                    print(topic_selections_of_group)
                    # Don't select topics that have already been selected by the group
                    if not topic_selections_of_group.filter(topic=topic_to_select.id).exists():
                        # Only select topics that can fit the group
                        if group_to_select.size <= topic_to_select.max_participants:
                            print("Select this topic: " + str(topic_to_select))


            # already_selected = False
            #
            # for known_selection in topic_selections_of_group:
            #     for selected_topic_id in selected_topics_ids:
            #         if int(selected_topic_id) == int(known_selection.topic.id):
            #             already_selected = True
            #             messages.error(request, _("Selection failed! You have already selected this topic."))
            #
            # if not already_selected:
            #     for selected_topic_id in selected_topics_ids:
            #         user_selection = TopicSelection()
            #         user_selection.group = existing_groups[0]
            #         user_selection.topic = models.Topic.objects.get(id=selected_topic_id)
            #         user_selection.collection_number = 0
            #         user_selection.save()
            #         if user_selection.topic.course.motivation_text:
            #             messages.warning(request,
            #                              _("You need to add a motivation text (when required) "
            #                                "to your selection in order to fully "
            #                                "complete your selection. You can do this on the \"My Selection\" page."))
            #         messages.success(request,
            #                          _("Your selection was successful! "
            #                            "You can find and edit your chosen topics on the "
            #                            "\"My Selection\" page."))







        # when any of the following args is in request
        elif any(["choose_topic" in request.POST, "open_group_select" in request.POST,
                  "select_topic" in request.POST, "select_with_chosen_group" in request.POST,
                  "open_group_create" in request.POST, "add_student" in request.POST,
                  "remove_student" in request.POST, "select_with_new_group" in request.POST]):

            if "choose_topic" in request.POST:
                data = str(request.POST.get("choose_topic")).split("|")
            # Make sure that only authenticated users with a student profile can select topics
            if request.user.is_authenticated and hasattr(request.user, "student"):
                # when deciding to choose a topic as a group
                if "open_group_select" in request.POST:
                    data = str(request.POST.get("open_group_select")).split("|")
                    args["open_group_select"] = True
                    args["groups"] = filter(
                        lambda x: 1 < x.size <= models.Topic.objects.get(id=data[0]).max_participants,
                        models.Group.objects.filter(students=request.user.student))

                # when selecting a topic alone
                elif "select_topic" in request.POST:
                    data = str(request.POST.get("select_topic")).split("|")
                    student_tu_id = str(request.user.student)

                    selected_topic_id = int(data[0])

                    existing_groups = []
                    for group in models.Group.objects.filter(students=student_tu_id):
                        if group.size == 1:
                            existing_groups.append(group)
                    # check if the user has not already got a hidden group for himself
                    if len(existing_groups) == 0:

                        group_of_student = Group()
                        group_of_student.save()
                        group_of_student.students.add(student_tu_id)

                        user_selection = TopicSelection()
                        user_selection.group = group_of_student
                        user_selection.topic = models.Topic.objects.get(id=selected_topic_id)
                        user_selection.collection_number = 0
                        user_selection.save()

                        messages.success(request,
                                         _("Your selection was successful! You can prioritize and edit your "
                                            "chosen topics on the 'Your Selection' page."))
                        if user_selection.topic.course.motivation_text:
                            messages.warning(request,
                                             _("You need to add a motivation text "
                                                "to your selection in order to fully complete your selection."))
                    # when the user already has a hidden group for himself
                    else:

                        topic_selections_of_group = models.TopicSelection.objects.filter(group=existing_groups[0].id)

                        already_selected = False

                        for known_selection in topic_selections_of_group:
                            if int(selected_topic_id) == int(known_selection.topic.id):
                                already_selected = True
                                messages.error(request, _("Selection failed! You have already selected this topic."))

                        if not already_selected:
                            user_selection = TopicSelection()
                            user_selection.group = existing_groups[0]
                            user_selection.topic = models.Topic.objects.get(id=selected_topic_id)
                            user_selection.collection_number = 0
                            user_selection.save()
                            messages.success(request,
                                             _("Your selection was successful! "
                                               "You can find and edit your chosen topics on the "
                                               "\"My Selection\" page."))
                            if user_selection.topic.course.motivation_text:
                                messages.warning(request,
                                                 _("You need to add a motivation text (when required) "
                                                    "to your selection in order to fully "
                                                    "complete your selection. You can do this on the \"My Selection\" page."))
                # when the user selects a group with an already existing group
                elif "select_with_chosen_group" in request.POST:
                    data = str(request.POST.get("select_with_chosen_group")).split("|")
                    selected_topic_id = data[0]
                    chosen_group_id = str(request.POST.get("group_options"))
                    if chosen_group_id != str(-1):
                        topic_selections_of_group = models.TopicSelection.objects.filter(group=chosen_group_id)
                        already_selected = False
                        for known_selection in topic_selections_of_group:
                            if int(selected_topic_id) == int(known_selection.topic.id):
                                already_selected = True
                                messages.error(request, _("Selection failed! You have already selected this topic."))

                        if not already_selected:
                            selection = TopicSelection()
                            selection.group = models.Group.objects.get(id=chosen_group_id)
                            selection.topic = models.Topic.objects.get(id=selected_topic_id)
                            selection.collection_number = 0
                            selection.save()

                            messages.success(request,
                                             _("Your selection was successful! "
                                                "You can find and edit your chosen topics on the "
                                                "\"My Selection\" page."))
                            if selection.topic.course.motivation_text:
                                messages.warning(request,
                                                 _("You need to add a motivation text (when required) "
                                                    "to your selection in order to fully "
                                                    "complete your selection. You can do this on the \"My Selection\" page."))

                    else:
                        args["open_group_select"] = True
                        args["groups"] = filter(
                            lambda x: 1 < x.size <= models.Topic.objects.get(id=data[0]).max_participants,
                            models.Group.objects.filter(students=request.user.student))
                        messages.error(request, "No group selected!")

                # when choosing to create a new group
                elif "open_group_create" in request.POST:
                    data = str(request.POST.get("open_group_create")).split("|")
                    args["members_in_new_group"] = [request.user.student.tucan_id]
                    args["open_group_create"] = True
                # adding a student to the new group draft
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
                                    messages.error(request, _("A student with the tucan id ") +
                                                   request.POST.get("new_student_id") +
                                                   _(" was not found."))
                            else:
                                messages.error(request, _("Your group would be too large for ") +
                                               str(models.Topic.objects.get(id=data[0]).title)
                                               + _(". Your group can only have a maximum of ") +
                                               str(models.Topic.objects.get(id=data[0]).max_participants)
                                               + _(" members."))
                        else:
                            messages.error(request, _("A student with the tucan id ") +
                                           request.POST.get("new_student_id") +
                                           _(" is already in the group."))

                    args["members_in_new_group"] = members_in_new_group
                    args["open_group_create"] = True
                # remove a student from group draft
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
                # when trying to select the topic and creating a new group
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
                        messages.error(request, _(f"Your group needs to contain more members than yourself!"))
                        exception = True

                    for groups_of_member in existing_groups:
                        if not exception:
                            for group in groups_of_member:
                                if set(members_in_new_group).issubset("".join(group.get_display.split(",")).split()) \
                                        and len(members_in_new_group) == \
                                        len("".join(group.get_display.split(",")).split()):
                                    messages.error(request, _(f"This group already exists!"))
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
                        selection.collection_number = 0
                        selection.save()

                        messages.success(request,
                                         _("Your selection was successful! "
                                           "You can find and edit your chosen topics on the "
                                           "\"My Selection\" page."))
                        if selection.topic.course.motivation_text:
                            messages.warning(request,
                                             _("You need to add a motivation text (when required) "
                                                "to your selection in order to fully "
                                                "complete your selection. You can do this on the \"My Selection\" page."))

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
    # initially show all faculties
    else:

        all_faculties = models.Course.objects.values("faculty").distinct().order_by("faculty")

        faculties = {}
        for faculty in all_faculties:
            course = models.Course.objects.filter(faculty=faculty["faculty"])
            faculties[faculty.get("faculty")] = course[0].get_faculty_display()

        args["faculties"] = faculties

    return render(request, template_name, args)


def check_profile(user):
    """Checks if an user has the attribute student

    :param user: The user of the content
    :type user: User
    :return: True if the user has the attribute student
    :rtype: Boolean
    """
    return hasattr(user, 'student')


@login_required
@user_passes_test(check_profile, login_url='/profile/', message="Please create a student profile before "
                                                                "selecting courses.")
def your_selection(request):
    """ View for "Your selection" page

    :param request: The given request
    :return: HttpRequest
    """
    template_name = 'frontend/your_selection.html'

    args = {}

    student_tucan_id = str(request.user.student)

    groups_of_student = []
    selections_of_groups = []

    # check if user has groups and collect them
    if models.Group.objects.filter(students=student_tucan_id).exists():
        groups_of_student = models.Group.objects.filter(students=student_tucan_id)
        for group in groups_of_student:
            selections_of_groups.append(models.TopicSelection.objects.filter(group=group.id))

    selections_of_collections_of_groups = {}

    for group in groups_of_student:
        selections_of_collections = {}
        for collection_number in range(0, group.collection_count + 1):
            selections_of_collections[collection_number] = []
            for selections in selections_of_groups:
                if len(selections) > 0:
                    if selections[0].group == group:
                        selections_of_collection = []
                        for selection in selections:
                            if collection_number == selection.collection_number:
                                selections_of_collection.append(selection)
                        selections_of_collections[collection_number] = sorted(selections_of_collection,
                                                                              key=lambda x: x.priority)
        selections_of_collections_of_groups[group] = selections_of_collections

    if request.method == "POST":
        # when removing a selected topic from a group
        if "remove_topic_button" in request.POST:
            data = str(request.POST.get("remove_topic_button")).split("|")
            selection_id = int(data[0])
            collection_number = int(data[1])
            group_of_selection = get_selection(selections_of_groups, selection_id).group

            priority_of_removed_topic = get_selection(selections_of_groups, selection_id).priority
            get_selection(selections_of_groups, selection_id).delete()
            selections_of_groups.clear()

            # show the groups and selected topics without the deleted one
            if models.Group.objects.filter(students=student_tucan_id).exists():
                groups_of_student = models.Group.objects.filter(students=student_tucan_id)
                for group in groups_of_student:
                    selections_of_groups.append(models.TopicSelection.objects.filter(group=group.id))

            del (selections_of_collections_of_groups[group_of_selection])[collection_number]

            selections_of_collections[collection_number] = []
            for selections in selections_of_groups:
                if len(selections) > 0:
                    if selections[0].group == group_of_selection:
                        selections_of_collection = []
                        for selection in selections:
                            if collection_number == selection.collection_number:
                                selections_of_collection.append(selection)
                        selections_of_collections[collection_number] = sorted(selections_of_collection,
                                                                              key=lambda x: x.priority)
            selections_of_collections_of_groups[group_of_selection] = selections_of_collections

            for group in groups_of_student:
                selections_of_collections = {}
                for collection_number_it in range(0, group.collection_count + 1):
                    selections_of_collections[collection_number_it] = []
                    for selections in selections_of_groups:
                        if len(selections) > 0:
                            if selections[0].group == group:
                                selections_of_collection = []
                                for selection in selections:
                                    if collection_number_it == selection.collection_number:
                                        selections_of_collection.append(selection)
                                selections_of_collections[collection_number_it] = sorted(selections_of_collection,
                                                                                         key=lambda x: x.priority)
                selections_of_collections_of_groups[group] = selections_of_collections

            # move up the remaining selection priorities to fill the gap left by the removed topic
            if priority_of_removed_topic != 0 and collection_number != 0:
                selections_in_same_collection = (selections_of_collections_of_groups[group_of_selection])[
                    collection_number]
                for selection in selections_in_same_collection:
                    if int(selection.priority) > int(priority_of_removed_topic):
                        selection.priority = int(selection.priority) - 1
                        selection.save()
                selections_of_collections_of_groups[group_of_selection][collection_number] = sorted(
                    selections_in_same_collection, key=lambda x: x.priority)

        # when pressing the button for editing the motivation text
        elif "edit_motivation_text_button" in request.POST:
            open_motivation_text_for_selection = int(request.POST.get("edit_motivation_text_button"))

            for selections_of_group in selections_of_groups:
                for selection in selections_of_group:
                    if selection.id == open_motivation_text_for_selection:
                        motivation_text_of_selection = selection.motivation
                        break

            args["open_motivation_text_for_selection"] = open_motivation_text_for_selection
            args["motivation_text_of_selection"] = motivation_text_of_selection
        # when saving the motivation text after editing it
        elif "save_motivation_text_button" in request.POST:
            save_motivation_text_for = int(request.POST.get("save_motivation_text_button"))
            motivation_text = str(request.POST.get("motivation_text"))

            for selections_of_group in selections_of_groups:
                for selection in selections_of_group:
                    if selection.id == save_motivation_text_for:
                        selection.motivation = motivation_text
                        selection.save()
                        messages.success(request, _("Your motivation text has been saved."))
                        break
        # when choosing to increase the priority of a selected topic
        elif "up_priority" in request.POST:
            data = str(request.POST.get("up_priority")).split("|")
            chosen_selection_id = int(data[0])
            collection_number = int(data[1])
            chosen_selection = get_selection(selections_of_groups, chosen_selection_id)

            selections_in_same_collection = (selections_of_collections_of_groups[chosen_selection.group])[
                collection_number]

            for selection in selections_in_same_collection:
                if selection.pk != chosen_selection.pk:
                    if selection.priority == chosen_selection.priority - 1:
                        selection.priority = chosen_selection.priority
                        selection.save()
                        chosen_selection.priority = chosen_selection.priority - 1
                        chosen_selection.save()
                        break
            selections_of_collections_of_groups[chosen_selection.group][collection_number] = sorted(
                selections_in_same_collection, key=lambda x: x.priority)

        # when choosing to decrease the priority of a selected topic
        elif "down_priority" in request.POST:
            data = str(request.POST.get("down_priority")).split("|")
            chosen_selection_id = int(data[0])
            collection_number = int(data[1])
            chosen_selection = get_selection(selections_of_groups, chosen_selection_id)

            selections_in_same_collection = (selections_of_collections_of_groups[chosen_selection.group])[
                collection_number]

            for selection in selections_in_same_collection:
                if selection.pk != chosen_selection.pk:
                    if selection.priority == chosen_selection.priority + 1:
                        selection.priority = chosen_selection.priority
                        selection.save()
                        chosen_selection.priority = chosen_selection.priority + 1
                        chosen_selection.save()
                        break
            selections_of_collections_of_groups[chosen_selection.group][collection_number] = sorted(
                selections_in_same_collection, key=lambda x: x.priority)
        elif "open_edit_collection" in request.POST:
            open_edit_collection_for_group = int(request.POST.get("open_edit_collection"))
            args["open_edit_collection_for_group"] = open_edit_collection_for_group
        elif "add_collection" in request.POST:
            for group in selections_of_collections_of_groups:
                if group.id == int(request.POST.get("add_collection")):
                    group.collection_count = group.collection_count + 1
                    group.save()
                    collections_of_group = selections_of_collections_of_groups[group]
                    collections_of_group[group.collection_count] = []
                    selections_of_collections_of_groups[group] = collections_of_group
                    args["open_edit_collection_for_group"] = group.id
                    break
        elif "remove_collection" in request.POST:
            data = str(request.POST.get("remove_collection")).split("|")
            for group, collections_of_group in selections_of_collections_of_groups.items():
                if group.id == int(data[0]):
                    for collection_number, selections in collections_of_group.items():
                        if collection_number == int(data[1]):
                            if not len(selections) > 0:
                                del (selections_of_collections_of_groups[group])[collection_number]
                                group.collection_count = group.collection_count - 1
                                group.save()
                                break
                            else:
                                for selection in selections:
                                    selection.delete()

                                del (selections_of_collections_of_groups[group])[collection_number]
                                group.collection_count = group.collection_count - 1
                                group.save()
                                break

                    collections_of_group_temp = {}
                    for collection_number, selections in collections_of_group.items():
                        if collection_number < int(data[1]):
                            collections_of_group_temp[collection_number] = collections_of_group[collection_number]
                        if collection_number > int(data[1]):
                            for selection in collections_of_group[collection_number]:
                                selection.collection_number = selection.collection_number - 1
                                selection.save()
                            collections_of_group_temp[collection_number - 1] = collections_of_group[collection_number]

                    selections_of_collections_of_groups[group] = collections_of_group_temp

            args["open_edit_collection_for_group"] = int(data[0])
        elif "ask_remove_collection" in request.POST:
            data = str(request.POST.get("ask_remove_collection")).split("|")
            args["ask_remove_group"] = int(data[0])
            args["ask_remove_collection"] = int(data[1])
            args["open_edit_collection_for_group"] = int(data[0])
        elif "change_collection" in request.POST:
            data = str(request.POST.get("change_collection")).split("|")
            result_change_collection = \
                change_collection(request, data, selections_of_collections_of_groups, False)
            selections_of_collections_of_groups = result_change_collection[0]
            args["error_message"] = result_change_collection[1]
            args["open_edit_collection_for_group"] = int(data[0])
        elif "assign_exclusives_to_matching_exclusive" in request.POST:
            """group = models.Group.objects.get(id=int(request.POST.get("assign_exclusives_to_matching_exclusive")))
            for selection in (selections_of_collections_of_groups[group])[0]:
                data = [(request.POST.get("assign_exclusives_to_matching_exclusive")), 0, selection.id, str(0)]
                selections_of_collections_of_groups = \
                    change_collection(request, data, selections_of_collections_of_groups, True)
            args["open_edit_collection_for_group"] = int(data[0])"""

    sorted_selections_of_groups = []
    # sort selected topics by priority
    for selections in selections_of_groups:
        sorted_selections_of_groups.append(sorted(selections, key=lambda x: x.priority))
    selections_of_groups = sorted_selections_of_groups

    motivation_text_required = []
    # only show the edit motivation text button when a motivation text is required
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
    # leave edit open when opening information
    if 'save_motivation_text_button' not in request.POST and 'cancel_motivation_save' not in request.POST \
            and not request.POST.get("open_motivation_text_for_selection") is None:

        open_motivation_text_for_selection = int(request.POST.get("open_motivation_text_for_selection"))

        for selections_of_group in selections_of_groups:
            for selection in selections_of_group:
                if selection.id == open_motivation_text_for_selection:
                    motivation_text_of_selection = selection.motivation
                    break

        args["open_motivation_text_for_selection"] = open_motivation_text_for_selection
        args["motivation_text_of_selection"] = motivation_text_of_selection
    # leave course information visible when pressing other buttons
    if (not request.POST.get("open_selection_info") is None) and "close_info_button" not in request.POST:
        info_selection = models.TopicSelection.objects.get(id=int(request.POST.get("open_selection_info")))
        args["info_selection"] = info_selection
        if str(request.POST.get("open_course_info")) == 'True':
            args["open_course_info"] = True
        else:
            args["open_course_info"] = False

    args["selections_of_collections_of_groups"] = selections_of_collections_of_groups
    args["motivation_text_required"] = motivation_text_required
    # opening the info of a selected topic
    if "info_button" in request.POST:
        info_selection = models.TopicSelection.objects.get(id=int(request.POST.get("info_button")))
        open_course_info = False

        args["info_selection"] = info_selection
        args["open_course_info"] = open_course_info
    # expanding the information the course of a selected topic
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


# Help functions of your_selection
def change_collection(request, data, selections_of_collections_of_groups, exclusive_matching):
    """ Tries to change the collection of a given selection if allowed

    :param request: The given request
    :param data: an array containing the group id, collection_number, selection id and target collection_number
    :param selections_of_collections_of_groups: the current state of selections
    :param exclusive_matching: boolean whether this function should try to match exclusives automatically
    :return: an array containing updated selections_of_collections_of_groups and a boolean for error handling
    """
    error = False
    if len("".join(data[3]).split()) > 0:
        for group, collections_of_group in selections_of_collections_of_groups.items():
            if group.id == int(data[0]):
                for collection_number, selections in collections_of_group.items():
                    if collection_number == int(data[1]):
                        for selection in selections:
                            if selection.id == int(data[2]) \
                                    and (selection.collection_number != int("".join(data[3]).split()[0])
                                         or exclusive_matching):
                                the_selection_is_exclusive = False
                                the_target_collection_has_exclusive_selections = False
                                matching_exclusive_collection_number = [False, 0]

                                if selection.topic.course.collection_exclusive:

                                    for group0, collections_of_group0 in selections_of_collections_of_groups.items():
                                        if group0.id == int(data[0]):
                                            for collection_number0, selections0 in collections_of_group.items():
                                                if collection_number0 > 0 and \
                                                        collection_number0 != selection.collection_number and \
                                                        len(selections0) > 0:
                                                    if selections0[0].topic.course == selection.topic.course:
                                                        matching_exclusive_collection_number = \
                                                            [True, collection_number0]

                                    if matching_exclusive_collection_number[0] \
                                            and int(data[3]) != matching_exclusive_collection_number[1]:
                                        data[3] = matching_exclusive_collection_number[1]
                                        messages.info(request, "Automatically assigned \"" + str(selection.topic.title)
                                                      + "\" to a matching collection")

                                    if not len(collections_of_group[int(data[3])]) == 0:
                                        if not collections_of_group[int(data[3])][0].topic.course \
                                               == selection.topic.course:
                                            the_selection_is_exclusive = True
                                            messages.error(request, "The target collection already has topics "
                                                                    "from a different course. The topic you are "
                                                                    "trying to assign can only be in a collection "
                                                                    "with topics from the same course.")
                                            error = True
                                else:
                                    if not len(collections_of_group[int(data[3])]) == 0:
                                        if not collections_of_group[int(data[3])][0].topic.course \
                                               == selection.topic.course:
                                            if collections_of_group[int(data[3])][0].topic.course.collection_exclusive:
                                                the_target_collection_has_exclusive_selections = True
                                                messages.error(request, "The target collection exclusively "
                                                                        "allows topics of course \""
                                                               + str(collections_of_group[int(data[3])][0].topic.course)
                                                               + "\".")
                                                error = True

                                if not the_selection_is_exclusive \
                                        and not the_target_collection_has_exclusive_selections:
                                    for selection_in_same_collection in selections:
                                        if selection_in_same_collection.priority > selection.priority:
                                            selection_in_same_collection.priority = \
                                                selection_in_same_collection.priority - 1
                                            selection_in_same_collection.save()

                                    selection.collection_number = int(data[3])
                                    selection.priority = len(collections_of_group[int(data[3])]) + 1
                                    selection.save()
                                    selections.remove(selection)
                                    collections_of_group[int(data[3])].append(selection)

                                    break
                        else:
                            continue
                        break
                else:
                    continue
                break

    return [selections_of_collections_of_groups, error]


def get_selection(selections_of_groups, chosen_selection_id):
    """ finds the selection in selections_of_groups that matches the given chosen_selection_id

    :param selections_of_groups: the given array containing all selections of all groups of a user
    :param chosen_selection_id: the given id of a selection
    :return: the selection with the id "chosen_selection_id" in "selections_of_groups"
    """
    for selections in selections_of_groups:
        for selection in selections:
            if int(selection.id) == int(chosen_selection_id):
                return selection


@login_required
@user_passes_test(check_profile, login_url='/profile/', message="Please create a student profile before "
                                                                "selecting courses.")
def groups(request):
    """ View for "Your Groups" page

    :param request: The given request
    :return: HttpRequest
    """
    template_name = 'frontend/groups.html'

    args = {}

    if request.method == "POST":
        # creating a new empty group
        if "open_create_new_group" in request.POST:
            args["members_in_new_group"] = [request.user.student.tucan_id]
            args["open_group_create"] = True
        # adding a student to the new group draft
        elif "add_student_to_new_group" in request.POST:
            members_in_new_group = []
            counter = 0
            while not (request.POST.get("member" + str(counter)) is None):
                members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                counter += 1

            if "".join(request.POST.get("new_student_id").split()) != "":
                if members_in_new_group.count(str(request.POST.get("new_student_id"))) == 0:
                    if models.Student.objects.filter(
                            tucan_id=request.POST.get("new_student_id")).exists():
                        members_in_new_group.insert(0, str(request.POST.get("new_student_id")))
                    else:
                        messages.error(request, "A student with the tucan id " +
                                       request.POST.get("new_student_id") +
                                       " was not found.")

                else:
                    messages.error(request, "A student with the tucan id " +
                                   request.POST.get("new_student_id") +
                                   " is already in the group.")

            args["members_in_new_group"] = members_in_new_group
            args["open_group_create"] = True
        # removing a student from the new group draft
        elif "new_group_remove_student" in request.POST:
            members_in_new_group = []
            counter = 0
            while not (request.POST.get("member" + str(counter)) is None):
                members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                counter += 1

            members_in_new_group.remove(str(request.POST.get("new_group_remove_student")))

            args["members_in_new_group"] = members_in_new_group
            args["open_group_create"] = True
        # creating the new group from the draft if there are no collisions
        elif "create_new_group" in request.POST:
            members_in_new_group = []
            counter = 0
            while not (request.POST.get("member" + str(counter)) is None):
                members_in_new_group.append(str(request.POST.get("member" + str(counter))))
                counter += 1

            existing_groups = []
            for member in members_in_new_group:
                if models.Group.objects.filter(students=member).exists():
                    existing_groups.append(models.Group.objects.filter(students=member))

            error = False

            if len(members_in_new_group) == 1:
                messages.error(request, f"Your group needs to contain more members than yourself!")
                error = True

            for groups_of_member in existing_groups:
                if not error:
                    for group in groups_of_member:
                        if set(members_in_new_group).issubset("".join(group.get_display.split(",")).split()) \
                                and len(members_in_new_group) == \
                                len("".join(group.get_display.split(",")).split()):
                            messages.error(request, f"This group already exists!")
                            error = True
                            break

            if not error:
                group = Group()
                group.save()

                counter = 0
                while not (request.POST.get("member" + str(counter)) is None):
                    group.students.add(
                        models.Student.objects.get(tucan_id=request.POST.get("member" + str(counter))))
                    counter += 1

                messages.success(request, "Group has been created.")
            else:
                args["open_group_create"] = True
                args["members_in_new_group"] = members_in_new_group
        # When pressing the button to delete a group
        if "ask_delete_group" in request.POST:
            chosen_group_for_deletion = int(request.POST.get("ask_delete_group"))
            args["chosen_group_for_deletion"] = chosen_group_for_deletion
        # Confirm the group deletion
        elif "delete_group" in request.POST:
            models.Group.objects.get(id=int(request.POST.get("delete_group"))).delete()
        # when clicking on the cog symbol to edit a group
        elif "open_edit" in request.POST:
            chosen_group_for_edit = int(request.POST.get("open_edit"))
            args["chosen_group_for_edit"] = chosen_group_for_edit
        # adding a student to the group if possible
        elif "add_student" in request.POST:
            if len("".join(request.POST.get("student_id")).split()) != 0:
                if models.Student.objects.filter(tucan_id=str(request.POST.get("student_id"))).exists():
                    if not models.Student.objects.get(
                            tucan_id=str(request.POST.get("student_id"))) in models.Group.objects.get(
                                        id=int(request.POST.get("add_student"))).students.all():
                        new_member_student = \
                            models.Student.objects.get(tucan_id=str(request.POST.get("student_id")))
                        group = models.Group.objects.get(id=int(request.POST.get("add_student")))
                        students_after_addition = []
                        for student in group.students.all():
                            students_after_addition.append(student)
                        students_after_addition.append(new_member_student)

                        colliding_group = models.Group.objects.filter(students=students_after_addition[0])
                        for student in students_after_addition:
                            colliding_group = colliding_group.filter(students=student.tucan_id)
                        for check_group in colliding_group:
                            if check_group.size != len(students_after_addition):
                                colliding_group = colliding_group.exclude(id=check_group.id)

                        if len(colliding_group) != 0:
                            messages.error(request, _("Adding {} "
                                                    f"would make this group a duplicate  "
                                                    "of an already existing one.").format(new_member_student))
                            args["error_message"] = True
                        else:
                            group.students.add(new_member_student)
                            group.save()
                    else:
                        student_id = str(request.POST.get("student_id"))
                        messages.error(request,
                                       f"{student_id} is already a member of this group")
                        args["error_message"] = True
                else:
                    student_id = str(request.POST.get("student_id"))
                    messages.error(request,
                                   f"A student with the Tucan ID {student_id} does not exist")
                    args["error_message"] = True

            args["chosen_group_for_edit"] = int(request.POST.get("add_student"))
        # arguments for the location of a message that shows when removing a student from a group of 2 members
        elif "ask_remove_student" in request.POST:
            data = str(request.POST.get("ask_remove_student")).split("|")
            args["chosen_student_for_removal"] = str(data[1])
            args["chosen_group_for_removal"] = int(data[0])
            args["chosen_group_for_edit"] = int(data[0])
        # Remove student from group if possible or delete the group if it is too small or a duplicate
        elif "remove_student" in request.POST:
            data = str(request.POST.get("remove_student")).split("|")
            group = models.Group.objects.get(id=int(data[0]))
            leaving_student = models.Student.objects.get(tucan_id=str(data[1]))

            if group.size == 2:
                group.delete()
            else:
                rest_students_after_removal = []
                for student in group.students.all():
                    if leaving_student.tucan_id != student.tucan_id:
                        rest_students_after_removal.append(student)
                colliding_group = models.Group.objects.filter(students=rest_students_after_removal[0])

                for student in rest_students_after_removal:
                    colliding_group = colliding_group.filter(students=student.tucan_id)
                for check_group in colliding_group:
                    if check_group.size > len(rest_students_after_removal):
                        colliding_group = colliding_group.exclude(id=check_group.id)

                if len(colliding_group) != 0:
                    if leaving_student.tucan_id == request.user.student.tucan_id:
                        group.delete()
                    else:
                        args["chosen_student_for_removal"] = leaving_student.tucan_id
                        args["chosen_group_for_removal"] = group.pk
                        args["chosen_group_for_edit"] = group.pk
                else:
                    group.students.remove(leaving_student)
                    group.save()

            args["chosen_group_for_edit"] = group.id

    groups_of_student = models.Group.objects.filter(students=request.user.student.tucan_id)
    members_of_groups = {}
    for group in groups_of_student:
        members = []
        for tucan_id in "".join(group.get_display.split(",")).split():
            members.append(User.objects.get(student=tucan_id))
        members_of_groups[group.id] = members

    args["groups_of_student"] = groups_of_student
    args["members_of_groups"] = members_of_groups

    return render(request, template_name, args)


def login_request(request, *given_template):
    """Login view

    :param request: The given request
    :param given_template: a string representing a template name
    :type request: HttpRequest
    """
    template_name = "registration/login.html"
    if given_template:
        template_name = given_template

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        # checks if the given login data is valid
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # proceeds to login the authenticated user
            if user is not None:
                login(request, user)
                messages.info(request, _("You are now logged in as {}.").format(username))
                return redirect("frontend:homepage")
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            messages.error(request, _("Invalid username or password."))
    form = UserLoginForm()
    return render(request, template_name, context={"login_form": form})


def logout_request(request):
    """Logout view

    :param request: The given request
    :type request: HttpRequest
    """
    # logs the user out
    logout(request)
    messages.info(request, _("You have successfully logged out."))
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
            messages.success(request, _("Registration successful."))
            return redirect("frontend:profile")
        messages.error(request, _("Unsuccessful registration. Invalid information."))
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
            messages.success(request, _("Student profile has been saved successfully."))
            return redirect("frontend:homepage")
        if hasattr(request.user, "student"):
            # maybe overwriting the current student is possible, but changing the primary key is troublesome
            messages.error(request, _("Student profile could not be saved. A user can only create one student."))
        else:
            messages.error(request, _("Saving unsuccessful. Invalid information."))
    form = NewStudentForm()
    return render(request=request, template_name="registration/profile.html", context={"profile_form": form})
