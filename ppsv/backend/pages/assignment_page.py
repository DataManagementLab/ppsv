from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from course.models import TopicSelection, Topic, CourseType, Course, Group
from backend.models import Assignment, possible_assignments_for_group, all_applications_from_group, \
    possible_assignments_for_topic


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
    if not TopicSelection.objects.filter(pk=application_id).exists():
        return False, "This assignment exists already"

    application = TopicSelection.objects.get(pk=application_id)

    # check if there is space in the slot for this application
    if application.group.size > application.topic.max_slot_size:
        return False, "No Space in Slot"
    new_slot = Assignment.objects.filter(topic=application.topic).filter(slot_id=slot_id)
    if new_slot.exists() and new_slot.get().open_places_in_slot_count < application.group.size:
        return False, "No Space in Slot"

    # check if group is not already assigned to another topic in the same collection
    if Assignment.objects.filter(accepted_applications__in=application.get_all_applications_in_collection).exists():
        return False, "The collection of this group is already satisfied"

    # make new assignment
    assignment = Assignment.objects.get_or_create(topic=application.topic, slot_id=slot_id)
    assignment[0].accepted_applications.add(application)
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

    if not TopicSelection.objects.filter(pk=application_id).exists():
        return False, "This Assignment does not exist"

    application = TopicSelection.objects.get(pk=application_id)

    if not Assignment.objects.filter(topic=application.topic, slot_id=slot_id).exists():
        return True, "Assignment does not exist"

    assignment = Assignment.objects.get(topic=application.topic, slot_id=slot_id)
    assignment.accepted_applications.remove(application)

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

    topic = Topic.objects.get(id=int(request.POST.get("topicID")))
    applications = []

    for application in TopicSelection.objects.filter(topic=topic):
        data = {
            'students': list(map(lambda x: x.pk, application.group.members)),
            'applicationID': application.id,
            'possibleAssignmentsForCollection': possible_assignments_for_group(application.group.id,
                                                                               application.collection_number),
            'collectionCount': TopicSelection.objects.filter(group=application.group,
                                                             collection_number=application.collection_number).count(),
            'preference': application.priority,
            'collectionFulfilled': Assignment.objects.filter(accepted_applications__group_id__in=[application.group],
                                                             accepted_applications__collection_number=application.collection_number).exists(),
        }
        assignment = Assignment.objects.filter(accepted_applications=application)
        if assignment.exists():
            data['slotID'] = assignment.get().slot_id
        else:
            data['slotID'] = -1
        applications.append(data)

    return JsonResponse(
        {
            'topicName': topic.title,
            'topicMinSlotSize': topic.min_slot_size,
            'topicMaxSlotSize': topic.max_slot_size,
            'topicSlots': topic.max_slots,
            'topicCourseName': topic.course.title,
            'applications': applications
        })


def handle_select_application(request):
    """
    Handles an application selection request.

    :return: the information about the group of the selected application.
    :rtype: JsonResponse
    """

    application = TopicSelection.objects.get(id=int(request.POST.get("applicationID")))
    return get_group_data(application.group_id, application.collection_number)


def handle_new_assignment(request):
    """
    Handles an assignment request by assigning the group to the slot of the topic.

    :return: If the assignment was successful and a corresponding text
    :rtype: JsonResponse
    """

    _new_assignment = new_assignment(int(request.POST.get("applicationID")), int(request.POST.get("slotID")))
    return JsonResponse({
        'requestStatus': _new_assignment[0],
        'text': _new_assignment[1]
    })


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
        return JsonResponse({
            'requestStatus': _remove_assignment[0],
            'text': _remove_assignment[1]
        })
    _new_assignment = new_assignment(application_id, new_slot_id)
    return JsonResponse({
        'requestStatus': _new_assignment[0],
        'text': _new_assignment[1]
    })


def handle_remove_assignment(request):
    """
    Handles a remove assignment request.

    :return: If the assignment was successfully removed
    :rtype: JsonResponse
    """

    _remove_assignment = remove_assignment(int(request.POST.get("applicationID")), int(request.POST.get("slotID")))

    return JsonResponse({
        'requestStatus': _remove_assignment[0],
        'text': _remove_assignment[1]
    })


def handle_get_possible_assignments_for_topic(request):
    application = TopicSelection.objects.get(pk=request.POST.get("applicationID"))
    _possibleAssignments = possible_assignments_for_group(application.group.id, application.collection_number)
    return JsonResponse({
        "possibleAssignments": _possibleAssignments,
    })


def handle_preselected_filters(request):
    """
    Handles preselected filters.

    :param request: the handled request
    :return: The rendered site with more arguments for preselected filters
    :rtype: render() object
    """
    args = {}
    filter_settings = {"CP": request.POST.getlist("cp"), "courseType": request.POST.getlist("courseType"),
                       "faculty": request.POST.getlist("faculty")}

    args['preselectedFilter'] = True
    args['filterSettings'] = filter_settings

    return render_site(request, args)


def handle_load_group_data(request):
    return get_group_data(request.POST.get("groupID"), request.POST.get("collectionID"))


# --- POST HANDLING HELPER --- #
def get_group_data(group_id, collection_id):
    group = Group.objects.get(id=group_id)

    members = []
    group_name = ""
    for member in group.members:
        members.append(member.tucan_id + ": " + member.firstname + ' ' + member.lastname)
        group_name += str(member) + ' '

    assignment_query = Assignment.objects.filter(accepted_applications__group__in=[group],
                                                 accepted_applications__collection_number=collection_id)
    assigned = assignment_query.get().id if assignment_query.exists() else None

    application_in_collection = []
    for application in all_applications_from_group(group_id, collection_id):
        topic = {
            'id': application.topic.id,
            'name': application.topic.title,
            'priority': application.priority,
            'freeSpace': possible_assignments_for_topic(application.topic)
        }
        application_in_collection.append(topic)

    return JsonResponse(
        {
            'selectedGroup': group_id,
            'selectedCollection': collection_id,
            'group_name': group_name,
            'members': members,
            'assigned': assigned,
            'collection': application_in_collection
        }
    )


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request

    """

    if "action" not in request.POST:
        raise ValueError("POST request didn't specify an action")

    action = request.POST.get("action")

    if action == "getPossibleAssignmentsForTopic":
        return handle_get_possible_assignments_for_topic(request)
    if action == "selectApplication":
        return handle_select_application(request)
    if action == "changeAssignment":
        return handle_change_assignment(request)
    if action == "newAssignment":
        return handle_new_assignment(request)
    if action == "removeAssignment":
        return handle_remove_assignment(request)
    if action == "preselectFilters":
        return handle_preselected_filters(request)
    if action == "selectTopic":
        return handle_select_topic(request)
    if action == "loadGroupData":
        return handle_load_group_data(request)

    raise ValueError(f"invalid request action: {action}")


# ----------Site rendering--------- #
def render_site(request, args=None):
    """
    handles the rendering of the assignment page.

    :param request: the handled request
    :param args: Arguments for rendering. When none given, an empty array is created

    :return: The rendered site
    :rtype: render() object
    """
    if args is None:
        args = {}
    template_name = 'backend/assignment.html'
    topics_of_courses = []
    topics = []
    last_course = ""
    if Topic.objects.exists():
        for topic in Topic.objects.filter(max_slots__gt=0):
            if last_course != topic.course.title:
                last_course = topic.course.title
                topics = []
                topics_of_course = {"course": topic.course, "topics": topics}
                topics_of_courses.append(topics_of_course)
            topics.append(topic)

    course_types = []
    for course_type in CourseType.objects.all():
        course_types.append(course_type.type)

    faculties = []
    for course in Course.objects.all():
        if course.faculty not in faculties:
            faculties.append(course.faculty)
    faculties.sort()

    args["topics_of_courses"] = topics_of_courses
    args["show_course"] = True
    args["course_types"] = course_types
    args["faculties"] = faculties
    args["range"] = range(1, 11)
    args["topicid"] = request.GET["topic"] if (request.method == "GET") and ("topic" in request.GET) else False
    args["groupid"] = request.GET["group"] if (request.method == "GET") and ("group" in request.GET) else False
    args["collectionid"] = request.GET["collection"] if (request.method == "GET") and (
            "collection" in request.GET) else False

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
