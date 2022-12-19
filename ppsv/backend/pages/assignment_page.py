from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from course.models import TopicSelection, Topic, CourseType, Course
from backend.models import Assignment, possible_assignments


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
            'possibleAssignmentsForCollection': possible_assignments(application.group.id,
                                                                     application.collection_number),
            'preference': application.priority,
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


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request

    """

    if "action" not in request.POST:
        raise ValueError("POST request didn't specify an action")

    action = request.POST.get("action")

    if action == "selectTopic":
        return handle_select_topic(request)

    if action == "newAssignment":
        return handle_new_assignment(request)

    if action == "changeAssignment":
        return handle_change_assignment(request)

    if action == "removeAssignment":
        return handle_remove_assignment(request)

    raise ValueError(f"invalid request action: {action}")


# ----------Main Function---------- #

def assignment_page(request):
    """The view for the assignment page.

    :param request: the given request send by the assignment html-page
    In case of the request methode being a 'POST' there are the following cases:
        select_topic:   the request was sent because a topic was selected; all relevant data regarding the rendering of
                        the webpage with the newly selected topic now displayed are retrieved from the database
        assign_group:    the request was sent because a group was assigned to a slot; the assignment will be stored
                            in the database if valid
        unassign_group:    the request was sent because a group was unassigned from a slot; the database entry corresponding
                            to the group assignment to the slot gets removed

    In case of the request methode not being a POST all topics will be returned grouped by their corresponding course.
    In case of the request specifying a user who is not allowed to access this download-page redirects to the
    login page.

    :return: a JsonResponse containing the information about the request if the request was a POST or a render()
    object otherwise
    """

    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:assignment_page'))

    template_name = 'backend/assignment.html'
    args = {}

    # check if the request is a post
    if request.method == "POST":
        return handle_post(request)

    # if the request is not a post return a render of the default page
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

    return render(request, template_name, args)
