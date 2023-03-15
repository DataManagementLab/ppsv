import traceback

from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.models import Assignment, AcceptedApplications, TermFinalization
from backend.pages.functions import possible_assignments_for_group, \
    get_or_none, \
    check_collection_satisfied, create_json_response, get_or_error, get_group_data, get_broken_slots, \
    get_score_and_chart_data
from backend.pages.home_page import handle_clear_slot
from course.models import TopicSelection, Topic, CourseType, Course, Term
from ppsv import settings


# ----------Database Interactions---------- #

def new_assignment(application_id, slot_id):
    """
    creates a new assignment and adds the application to it. If a fitting assignment already exists the group is added
    to the existing assignment.

    :param application_id: the id application to assign
    :type application_id: int
    :param slot_id: the id of the slot of the new assignment
    :type slot_id: int

    :return: True, if the assignment got created and a text describing it
    :rtype: (Boolean, String)
    """

    # check if the application exists
    application = get_or_error(TopicSelection, pk=application_id, topic__course__term=Term.get_active_term())

    # check if there is space in the slot for this application
    if application.group.size > application.topic.max_slot_size:
        return False, "This is an illegal application for this slot: it does not fit into it!"

    # check if group is not already assigned to another topic in the same collection
    if check_collection_satisfied(application):
        return False, "The collection of this group is already satisfied"

    # get or make the slot
    try:
        assignment = Assignment.objects.get_or_create(topic=application.topic,
                                                      slot_id=slot_id,
                                                      topic__course__term=Term.get_active_term())
    except MultipleObjectsReturned as e:
        raise ValidationError(f"Error in getting an object from {Assignment}: \n {e}")

    assignment = assignment[0]
    if assignment.open_places_in_slot_count < application.group.size:
        return False, "No Space in Slot"

    # make new assignment
    accepted_application = AcceptedApplications.objects.get_or_create(assignment=assignment,
                                                                      topic_selection=application)
    if not accepted_application[1]:
        return False, "Could not save the assignment"
    return True, "Saved to Database"


def remove_assignment(application_id, slot_id):
    """
    removes the application from this assignment and deletes the assignment if this was the last application

    :param application_id: the id of the application to remove
    :type application_id: int
    :param slot_id: the id of the slot to remove the application from
    :type slot_id: int

    :return: True, if the assignment got delete and a text describing it
    :rtype: (Boolean, String)
    """

    # get application
    application = get_or_error(TopicSelection, pk=application_id, topic__course__term=Term.get_active_term())

    # get slot
    assignment = get_or_error(Assignment, topic=application.topic, slot_id=slot_id,
                              topic__course__term=Term.get_active_term())

    # get assignment
    accepted_application = get_or_error(AcceptedApplications, assignment=assignment, topic_selection=application)

    # check if slot locked
    if assignment.finalized_slot > 0:
        return False, "This slot is locked and can not be changed"

    # check if assignment locked
    if accepted_application.finalized_assignment:
        return False, "This assignment is locked and cannot be changed"

    # delete the assignment
    assignment.accepted_applications.remove(application)

    # delete the slot if it is empty
    if assignment.accepted_applications.count() == 0:
        assignment.delete()
    return True, "Assignment deleted"


# ----------POST Handling---------- #

def handle_select_topic(request):
    """
    Handles a topic selection request.

    :return: the information about the slots of the selected topic.
    :rtype: JsonResponse
    """

    # get topic
    topic = get_or_error(Topic, id=int(request.POST.get("topicID")))

    # get query applications for topic
    applications = TopicSelection.objects.filter(topic=topic, topic__course__term=Term.get_active_term())

    # get query assignments for topic
    assignments = Assignment.objects.filter(topic=topic, topic__course__term=Term.get_active_term())

    # load all applications data
    _applications = []
    for application in applications:
        # application data
        data = {
            'students': list(map(lambda x: x.pk, application.group.members)),
            'applicationID': application.id,
            'possibleAssignmentsForCollection': possible_assignments_for_group(application.group.id,
                                                                               application.collection_number),
            'collectionCount': TopicSelection.objects.filter(group=application.group,
                                                             collection_number=application.collection_number,
                                                             topic__course__term=Term.get_active_term()).count(),
            'preference': application.priority,
            'collectionFulfilled': check_collection_satisfied(application),
            'groupID': application.group.id,
            'collectionID': application.collection_number,
        }

        # accepted application data
        accepted_application = get_or_none(AcceptedApplications,
                                           assignment__topic=topic,
                                           assignment__topic__course__term=Term.get_active_term(),
                                           topic_selection=application)
        if accepted_application is None:
            data['finalizedAssignment'] = False
            data['slotID'] = -1
        else:
            data['finalizedAssignment'] = accepted_application.finalized_assignment
            data['slotID'] = accepted_application.assignment.slot_id

        _applications.append(data)

    # load slot data
    term_finalized = TermFinalization.is_finalized(Term.get_active_term())
    slots_finalized = [int(term_finalized) for _ in range(topic.max_slots)]
    if not term_finalized:
        counter = 0
        for assignment in assignments:
            slots_finalized[counter] = assignment.finalized_slot

    return JsonResponse(
        {
            'topicName': topic.title,
            'topicMinSlotSize': topic.min_slot_size,
            'topicMaxSlotSize': topic.max_slot_size,
            'topicSlotsFinalized': slots_finalized,
            'topicSlots': topic.max_slots,
            'topicCourseName': topic.course.title,
            'applications': _applications
        })


def handle_select_application(request):
    """
    Handles an application selection request.

    :return: the information about the group of the selected application.
    :rtype: JsonResponse
    """
    # get topic
    application = get_or_error(TopicSelection,
                               id=int(request.POST.get("applicationID")),
                               topic__course__term=Term.get_active_term())

    return get_group_data(application.group_id, application.collection_number)


def handle_new_assignment(request):
    """
    Handles an assignment request by assigning the group to the slot of the topic.

    :return: If the assignment was successful and a corresponding text
    :rtype: JsonResponse
    """

    _new_assignment = new_assignment(int(request.POST.get("applicationID")), int(request.POST.get("slotID")))
    return create_json_response(_new_assignment[0], _new_assignment[1])


def handle_change_assignment(request):
    """
    Handles a request to change an assignment.

    :return: the response of the change
    :rtype: JsonResponse
    """

    application_id = int(request.POST.get("applicationID"))
    old_slot_id = int(request.POST.get("oldSlotID"))
    new_slot_id = int(request.POST.get("newSlotID"))
    _remove_assignment = remove_assignment(application_id, old_slot_id)
    # couldn't remove the old selection
    if not _remove_assignment[0]:
        return create_json_response(False, _remove_assignment[1])
    _new_assignment = new_assignment(application_id, new_slot_id)
    return create_json_response(_new_assignment[0], _new_assignment[1])


def handle_remove_assignment(request):
    """
    Handles a remove assignment request.

    :return: If the assignment was successfully removed
    :rtype: JsonResponse
    """

    _remove_assignment = remove_assignment(int(request.POST.get("applicationID")), int(request.POST.get("slotID")))
    return create_json_response(_remove_assignment[0], _remove_assignment[1])


def handle_remove_other_assignment(request):
    """
    Handle a remove assignment other request. This is used if we want to override an already assigned application

    :return: If the assignment was successfully removed
    :rtype: JsonResponse
    """
    # get application
    application = get_or_error(TopicSelection, id=request.POST.get("applicationID"),
                               topic__course__term=Term.get_active_term())

    # get accepted application
    accepted_application = get_or_error(AcceptedApplications,
                                        topic_selection__group=application.group,
                                        topic_selection__collection_number=application.collection_number,
                                        topic_selection__topic__course__term=application.topic.course.term)

    # delete accepted application
    accepted_application.delete()
    return create_json_response(True, "Removed Assignment")


def handle_get_possible_assignments_for_topic(request):
    """
    Handles the request for getting possible assignments of a topic.

    :param request: the handled request
    return: the possible assignments for a topic
    :rtype: JsonResponse
    """
    application = get_or_error(TopicSelection, pk=request.POST.get("applicationID"),
                               topic__course__term=Term.get_active_term())

    return JsonResponse({
        "possibleAssignments": possible_assignments_for_group(application.group.id, application.collection_number),
        "collectionFulfilled": check_collection_satisfied(application)
    })


def handle_load_group_data(request):
    """

    :param request: the handled request
    :return: The group data of the group and collection specified by the request
    :rtype: JsonResponse
    """
    return get_group_data(request.POST.get("groupID"), request.POST.get("collectionID"))


def handle_change_finalized_value_slot(request):
    """
    Handles a change of the finalized value of a slot. If the term is finalized this will always return the admin locked status

    :param request: the handled request
    :return: If the finalized_slot value was changed successfully, the new finalized_slot value, a status and text
    depicting if and how the finalized_slot value was changed
    :rtype: JsonResponse
    """

    assignment = Assignment.objects.get_or_create(slot_id=request.POST.get("slotID"),
                                                  topic_id=request.POST.get("slotTopicID"))[0]
    if TermFinalization.is_finalized(Term.get_active_term()):
        assignment.finalized_slot = 2

    old_finalized_value = assignment.finalized_slot

    if old_finalized_value >= 2:
        finalization_changed = False
        finalization_value = old_finalized_value
        finalization_changed_status = "bad"
        finalization_changed_text = "Slot can't be unlocked"
    elif (assignment.assigned_student_to_slot_count < assignment.topic.min_slot_size) and (old_finalized_value == 0):
        finalization_changed = False
        finalization_value = old_finalized_value
        finalization_changed_status = "bad"
        finalization_changed_text = "Only slots with the minimum amount of needed applications can be locked"
    else:
        assignment.finalized_slot = request.POST.get("newFinalized")
        assignment.save()
        finalization_changed = True
        finalization_value = request.POST.get("newFinalized")
        finalization_changed_status = "good"
        finalization_changed_text = "Slot has been locked" if (
                old_finalized_value == 0) else "Slot has been unlocked"

    return JsonResponse({
        'finalizationChanged': finalization_changed,
        'finalizationValue': finalization_value,
        'finalizationChangedStatus': finalization_changed_status,
        'finalizationChangedText': finalization_changed_text,
    })


def handle_change_finalized_value_application(request):
    """
    Handles a change of the finalized value of an application.

    :param request: the handled request
    :return: If the finalized_assignment value was changed successfully, the new finalized_assignment value, a status
    and text depicting if and how the finalized_assignment value was changed
    :rtype: JsonResponse
    """

    assignment_slot = get_or_error(Assignment,
                                   slot_id=request.POST.get("slotID"),
                                   topic_id=request.POST.get("slotTopicID"),
                                   topic__course__term=Term.get_active_term())
    accepted_application = get_or_error(AcceptedApplications,
                                        topic_selection=request.POST.get("applicationID"),
                                        assignment=assignment_slot)

    old_finalized_value_slot = assignment_slot.finalized_slot

    if old_finalized_value_slot < 2:

        old_finalized_value_application = accepted_application.finalized_assignment
        accepted_application.finalized_assignment = not old_finalized_value_application
        accepted_application.save()
        finalization_changed = True
        finalization_value = accepted_application.finalized_assignment
        finalization_changed_status = "good"
        finalization_changed_text = "Assignment has been locked" if not old_finalized_value_application else "Assignment has been unlocked"
    else:
        finalization_changed = False
        finalization_value = accepted_application.finalized_assignment

        finalization_changed_status = "bad"
        finalization_changed_text = "Application can't be (un)locked"

    return JsonResponse({
        'finalizationChanged': finalization_changed,
        'finalizationValue': finalization_value,
        'finalizationChangedStatus': finalization_changed_status,
        'finalizationChangedText': finalization_changed_text,
    })


def handle_get_statistic_data(request):
    """
    Returns the statistic data for the current term
    """
    data = get_score_and_chart_data(request)
    broken_slots = get_broken_slots()

    return JsonResponse({
        'groups': data[0],
        'students': data[1],
        "score": data[2],
        "brokenSlots": len(broken_slots[0]) + (len(broken_slots[1])),
        "notAssignedGroups": data[3]
    })

def handle_get_topics_filtered(request):
    """
    Returns the statistic data for the current term.
    This method will also apply the given filters for CP, course type and faculty.
    """
    min_cp = int(request.POST.get('minCP'))
    max_cp = int(request.POST.get('maxCP'))
    course_types = request.POST.getlist('courseTypes[]')
    faculties = request.POST.getlist('faculties[]')

    if max_cp == -1:
        topics = list(Topic.objects.filter(course__cp__gte=min_cp,
                                           course__type__in=course_types,
                                           course__faculty__in=faculties,
                                           course__term=Term.get_active_term()))
    else:
        topics = list(Topic.objects.filter(course__cp__range=(min_cp, max_cp),
                                           course__type__in=course_types,
                                           course__faculty__in=faculties,
                                           course__term=Term.get_active_term()))

    filter_type = int(request.POST.get('special'))
    accepted_application_dict = AcceptedApplications.get_collection_dict()

    filter_topic_ids = []

    for topic in topics:
        if filter_type == 1:
            if Assignment.has_open_places(topic) != 0:
                filter_topic_ids.append(topic.id)
        if filter_type == 2:
            for application in TopicSelection.objects.filter(topic=topic):
                if application.dict_key not in accepted_application_dict:
                    filter_topic_ids.append(topic.id)
                    break

    return JsonResponse({
        'filteredTopics': filter_topic_ids,
    })


def handle_get_bulk_applications_update(request):
    """returns the status for all applications of the request"""

    app_ids = request.POST.getlist('applicationIDs[]')
    app_data = {}
    for app in TopicSelection.objects.filter(pk__in=app_ids):
        app_data[app.pk] = {
            'possibleAssignments': possible_assignments_for_group(app.group, app.collection_number),
            'collectionFulfilled': check_collection_satisfied(app)
        }
    return JsonResponse(app_data)


def handle_groups_by_prio():
    """
    returns a json object with a list of groups (value) per prio (key)
    0 stands for not assigned, 6 for prio over 5
    """
    group_by_prio = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    accepted_application_dict = AcceptedApplications.get_collection_dict()
    for app_key in TopicSelection.get_collection_dict():
        group_id_collection_id_key = (app_key[0].id, app_key[1])
        if app_key in accepted_application_dict:
            if accepted_application_dict[app_key].priority > 5:
                group_by_prio[6].append(group_id_collection_id_key)
            else:
                group_by_prio[accepted_application_dict[app_key].priority].append(group_id_collection_id_key)
        else:
            group_by_prio[0].append(group_id_collection_id_key)

    return JsonResponse(group_by_prio)


def handle_get_broken_slots():
    """
    returns two lists of all broken slots each with (topicID, slotid, String of the Slot, Error Message) Tuples.
    The first list are slots that are non-critical errors, and the second are slots that are critical errors and could
    cause issues
    """
    return JsonResponse({
        'brokenSlots': get_broken_slots()
    })


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request

    """
    action = ""
    try:
        if "action" not in request.POST:
            return HttpResponse(status=501,
                                content="POST request didn't specify an action. Please report this and the actions "
                                        "you took to get this message to the administrator!")

        action = request.POST.get("action")

        if action == "getBulkApplicationsUpdate":
            return handle_get_bulk_applications_update(request)
        if action == "selectApplication":
            return handle_select_application(request)
        if action == "changeAssignment":
            return handle_change_assignment(request)
        if action == "newAssignment":
            return handle_new_assignment(request)
        if action == "removeAssignment":
            return handle_remove_assignment(request)
        if action == "removeOtherAssignment":
            return handle_remove_other_assignment(request)
        if action == "getStatisticData":
            return handle_get_statistic_data(request)
        if action == "selectTopic":
            return handle_select_topic(request)
        if action == "loadGroupData":
            return handle_load_group_data(request)
        if action == "groupsByPrio":
            return handle_groups_by_prio()
        if action == "getBrokenSlots":
            return handle_get_broken_slots()
        if action == "clearSlot":
            return handle_clear_slot(request)
        if action == "getTopicsFiltered":
            return handle_get_topics_filtered(request)
        if action == "changeFinalizedValueSlot":
            return handle_change_finalized_value_slot(request)
        if action == "changeFinalizedValueApplication":
            return handle_change_finalized_value_application(request)

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took "
                                    f"to get this message to an administrator!")

    except Exception as e:
        if settings.DEBUG:
            print(traceback.format_exc())
        return HttpResponse(status=500, content=f"request {action} caused an exception: \n {e}")


# ----------Site rendering--------- #
def render_site(request):
    """
    handles the rendering of the assignment page.
    parses additional information in the address and handles it accordingly

    :param request: the handled request
    :param args: Arguments for rendering. When none given, an empty array is created

    :return: The rendered site
    :rtype: render() object
    """
    args = {}
    template_name = 'backend/assignment.html'
    topics_of_courses = []
    topics = []
    last_course = ""
    for topic in Topic.objects.filter(max_slots__gt=0, course__term=Term.get_active_term()):
        if last_course != topic.course.title:
            last_course = topic.course.title
            topics = []
            topics_of_course = {"course": topic.course, "topics": topics}
            topics_of_courses.append(topics_of_course)
        topics.append(topic)

    course_types = []
    for course_type in CourseType.objects.all():
        course_types.append(course_type)

    faculties = []
    for course in Course.objects.all():
        if course.faculty not in faculties:
            faculties.append(course.faculty)
    faculties.sort()

    # load information from url
    topic_ids = False
    group_id = False
    collection_id = False
    if request.method == "GET":
        if "topic" in request.GET and request.GET["topic"].split(" ")[0] != '-1':
            topic_ids = request.GET["topic"].split(" ")
        if "group" in request.GET and request.GET["group"] != '-1':
            group_id = request.GET["group"]
        if "collection" in request.GET and request.GET["collection"] != '-1':
            collection_id = request.GET["collection"]

    args["topics_of_courses"] = topics_of_courses
    args["course_types"] = course_types
    args["faculties"] = faculties
    args["range"] = range(1, 11)
    args["topicids"] = topic_ids
    args["groupid"] = group_id
    args["collectionid"] = collection_id

    return render(request, template_name, args)


# ----------Main Function---------- #

def assignment_page(request):
    """The view for the assignment page.

    :param request: the given request send by the assignment html-page
    In case of the request type being a 'POST' it will be handled by the handle_post method

    In case of the request method not being a POST all topics will be returned grouped by their corresponding course.
    In case of the request specifying a user who is not allowed to access this download-page redirects to the
    login page.

    :return: a JsonResponse containing the information about the request if the request was a POST or a render()
    object otherwise
    """

    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:assignment_page'))

    # check if the request is a post
    if request.method == "POST":
        return handle_post(request)

    # if the request is not a post return a render of the default page
    return render_site(request)
