from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from course.models import TopicSelection, Topic
from backend.models import Assignment, remaining_selections_count


# ----------Database Interactions----------

def check_switch_application(application_id, new_slot_id):
    """
    checks if the given application can be assigned to the given slot.

    :param application_id: the application to check
    :type application_id: int
    :param new_slot_id: the id of the slot to assign the application to
    :type new_slot_id: int

    :return: True, if the assignment is possible, otherwise False and a text describing the result
    :rtype: (Boolean, String)
    """
    # check if the application exists
    if not TopicSelection.objects.filter(pk=application_id).exists():
        return False, "No selection for this topic exists"

    application = TopicSelection.objects.get(pk=application_id)

    # check if there is space in the slot for this application
    if application.group.size > application.topic.max_slot_size:
        return False, "No Space in Slot"
    new_slot = Assignment.objects.filter(topic=application.topic).filter(slot_id=new_slot_id)
    if new_slot.exists() and new_slot.get().open_places_in_slot_count < application.group.size:
        return False, "No Space in Slot"

    # check if group is not already assigned to another topic in the same collection
    topics = []
    for t in application.get_all_applications_in_collection:
        topics.append(t.topic)
    q = Assignment.objects.filter(groups__in=[application.group], topic__in=topics).exclude(topic=application.topic)
    if q.count() > 0:
        return False, "The collection of this group is already satisfied with: " + str(q.first()),
    return True, "This assignment can be saved"


def new_assignment(application_id, slot_id):
    """
    creates a new assignment and adds the group to it. If a fitting assignment already exists the group is added
    to the existing assignment.

    :param topic_id: the id of the topic of the new assignment
    :type topic_id: int
    :param group_id: the id of the group of the new assignment
    :type group_id: int
    :param slot_id: the id of the slot of the new assignment
    :type slot_id: int

    :return: True, if the assignment got created and a text describing it
    :rtype: (Boolean, String)
    """

    application = TopicSelection.objects.get(pk=application_id)

    assignment = Assignment.objects.get_or_create(topic=application.topic, slot_id=slot_id)[0]
    assignment.groups.add(application.group)
    return True, "Saved to Database"


def remove_assignment(application_id, slot_id):
    """
    removes the group from the slot of the topic and deletes the assignment if no other group is assigned

    :param application_id: the id of the application to remove the group from
    :type application_id: int
    :param slot_id: the id of the group to remove from the topic
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
    assignment.groups.remove(application.group)

    if assignment.groups.count() == 0:
        assignment.delete()

    return True, "Assignment deleted"


# ----------POST Handling----------

def handle_select_topic(request):
    """
    Handles a topic selection request.

    :return: the information about the slots of the selected topic.
    :rtype: JsonResponse
    """

    topic = Topic.objects.get(id=int(request.POST.get("topic_id")))

    assignments = []
    applications = []
    for topicSelection in TopicSelection.objects.filter(topic=topic.id):
        temp = {
            'students': list(map(lambda x: x.pk, topicSelection.group.members)),
            'applicationID': topicSelection.id,
            'allRemainingApplication': remaining_selections_count(topicSelection.group.id,
                                                                  topicSelection.collection_number),
            'preference': topicSelection.priority,
        }

        if Assignment.objects.filter(topic=topicSelection.topic,
                                     groups__in=[topicSelection.group]).exists():
            assignments.append(temp)
            temp['slotID'] = Assignment.objects.filter(topic=topicSelection.topic,
                                                       groups__in=[topicSelection.group]).get().slot_id
        else:
            applications.append(temp)

    return JsonResponse(
        {
            'topicName': topic.title,
            'topicMinSlotSize': topic.min_slot_size,
            'topicMaxSlotSize': topic.max_slot_size,
            'topicSlots': topic.max_slots,
            'topicCourseName': topic.course.title,
            'assignments': assignments,
            'applications': applications
        })


def handle_new_assignment(request):
    """
    Handles an assignment request by assigning the group to the slot of the topic.

    :return: If the assignment was successful and a corresponding text
    :rtype: JsonResponse
    """

    application_id = int(request.POST.get("applicationID"))
    slot_id = int(request.POST.get("slotID"))
    _check_application = check_switch_application(application_id, slot_id)
    if _check_application[0]:
        _save_new_assignment = new_assignment(application_id, slot_id)
        return JsonResponse({
            'requestStatus': _save_new_assignment[0],
            'text': _save_new_assignment[1]
        })
    else:
        return JsonResponse({
            'requestStatus': _check_application[0],
            'text': _check_application[1]
        })


def handle_change_assignment(request):
    """
    Handles a request to change an assignment.

    :return: If the change was successful
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
    _check_application = check_switch_application(application_id, new_slot_id)
    # we can do the change
    if _check_application[0]:
        _new_assignment = new_assignment(application_id, new_slot_id)
        return JsonResponse({
            'requestStatus': _check_application[0],
            'text': _new_assignment[1]
        })
    # revert back we cant do the new assignment
    else:
        _new_assignment = new_assignment(application_id, old_slot_id)
        return JsonResponse({
            'requestStatus': _check_application[0],
            'text': _check_application[1]
        })


def handle_remove_assignment(request):
    """
    Handles an unassignment request.

    :return: If the unassignment was successful
    :rtype: JsonResponse
    """

    application_id = int(request.POST.get("applicationID"))
    slot_id = int(request.POST.get("slotID"))

    _remove_assignment = remove_assignment(application_id, slot_id)

    return JsonResponse({
        'requestStatus': _remove_assignment[0],
        'text': _remove_assignment[1]
    })


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request
    :return: the return of the called function
    :rtype: JsonResponse
    :raise: ValueError, if no action is specified in the POST or the given action isn't handled
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


# ----------Main Function----------

def assignment_page(request):
    """The view for the assignment page.

    :param request: the given request send by the assignment html-page
    In case of the request methode being a 'POST' there are the following cases specified in the action field:
        select_topic:     the request was sent because a topic was selected; all relevant data regarding the rendering of
                          the webpage with the newly selected topic now displayed are retrieved from the database
        newAssignment:     the request was sent because a group was assigned to a slot; the assignment will be stored
                           in the database if valid
        changeAssignment:  the request was sent because a group was assigned to different slot and/or topic;
                           the assignment will be stored in the database if valid
        removeAssignment:  the request was sent because a group was unassigned from a slot; the database entry corresponding
                           to the group assignment to the slot gets removed

    In case of the request methode not being a POST all topics will be returned grouped by their corresponding course.
    In case of the request specifying a user who is not allowed to access this download-page redirects to the
    login page.

    :return: a JsonResponse containing the information about the request if the request was a POST or a render()
    object otherwise
    :rtype: JsonResponse or HttpResponse
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

    args["topics_of_courses"] = topics_of_courses
    args["show_course"] = True

    return render(request, template_name, args)
