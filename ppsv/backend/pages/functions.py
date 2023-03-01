from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.http import JsonResponse

from backend.models import Assignment
from course.models import TopicSelection, Term, Group


# --- GENERAL FUNCTIONS FOR POST REQUESTS --- #

def get_or_none(classmodel, **kwargs):
    """
    gets an object or throws an error if there are more than one in the database. If there are none in the database
    it will return None
    """
    try:
        return classmodel.objects.get(**kwargs)
    except MultipleObjectsReturned:
        raise ValidationError(f"Error in getting an object from {classmodel} with filters {kwargs}: "
                              f"Multiple objects found. \n Try to clear the slot, or contact an administrator.")
    except classmodel.DoesNotExist:
        return None


def get_or_error(classmodel, **kwargs):
    """
    gets an object or throws an error if there is none or more than one in the database
    """
    temp = get_or_none(classmodel, **kwargs)
    if temp is None:
        raise ValidationError(f"Error in getting an object from {classmodel} with filters {kwargs}: No objects found. "
                              f"\n Try to clear the slot, or contact an administrator.")
    return temp


def create_json_response(success, msg):
    """Creates a json response with request status and text"""
    return JsonResponse({
        'requestStatus': success,
        'text': msg
    })


def handle_get_score_data(request):
    """Creates the data for the score and broken slots.

        :return: The data for the score and broken slots.
        :rtype: JsonResponse
        """
    application_query, assignment_query = get_filtered_query_from_request(request)

    # score
    score = 0
    accepted_applications = []
    for assignment in assignment_query.all():
        for accepted_application in assignment.accepted_applications.all():
            score += get_score_for_assigned(accepted_application.priority)
            accepted_applications.append((accepted_application.group, accepted_application.collection_number))

    for application in application_query.all():
        if (application.group, application.collection_number) not in accepted_applications:
            score += get_score_for_not_assigned()

    # max score
    max_score = 0
    handled_applications = []
    for application in application_query.all():
        if (application.group, application.collection_number) not in handled_applications:
            handled_applications.append((application.group, application.collection_number))
            max_score += get_score_for_assigned(1)

    # broken slots
    broken_slots = get_broken_slots()

    return JsonResponse({
        "score": score,
        "maxScore": max_score,
        "brokenSlots": len(broken_slots[0]) + (len(broken_slots[1])),
    })


def get_filtered_query_from_request(request):
    """
    Filters the DB for the given request and returns to queries, one for applications and one for assignments
    """
    min_cp = int(request.POST.get('minCP'))
    max_cp = int(request.POST.get('maxCP'))
    course_types = request.POST.getlist('courseTypes[]')
    faculties = request.POST.getlist('faculties[]')

    if max_cp == -1:
        assignment_query = Assignment.objects.filter(topic__course__cp__gte=min_cp,
                                                     topic__course__type__in=course_types,
                                                     topic__course__faculty__in=faculties,
                                                     topic__course__term=Term.get_active_term())
        application_query = TopicSelection.objects.filter(topic__course__cp__gte=min_cp,
                                                          topic__course__type__in=course_types,
                                                          topic__course__faculty__in=faculties,
                                                          topic__course__term=Term.get_active_term())
    else:
        assignment_query = Assignment.objects.filter(topic__course__cp__range=(min_cp, max_cp),
                                                     topic__course__type__in=course_types,
                                                     topic__course__faculty__in=faculties,
                                                     topic__course__term=Term.get_active_term())
        application_query = TopicSelection.objects.filter(topic__course__cp__range=(min_cp, max_cp),
                                                          topic__course__type__in=course_types,
                                                          topic__course__faculty__in=faculties,
                                                          topic__course__term=Term.get_active_term())
    return application_query, assignment_query


def possible_assignments_for_group(group_id, collection_number):
    """possible applications in collection
    :return: the number of possible applications of this group for the given collection
    :rtype: int
    """

    all_applications = all_applications_from_group(group_id, collection_number)
    possible_assignments_for_group = 0
    for application in all_applications:
        query_assignments_for_topic = Assignment.objects.filter(topic=application.topic,
                                                                topic__course__term=Term.get_active_term())
        if query_assignments_for_topic.count() < application.topic.max_slots:
            possible_assignments_for_group += 1
            continue
        for slot in query_assignments_for_topic:
            if slot.open_places_in_slot_count >= application.group.size:
                possible_assignments_for_group += 1
                break
    return possible_assignments_for_group


def possible_assignments_of_group_to_topic(topic, group):
    """
    Returns all assignments than ce be assigned to the given topic without exceeding its maximum slot size
    :param topic: the topic the search the possible assignments of
    :param group: the group to search the possible assignments for
    """
    open_assignment_count = topic.max_slots
    for assignment in Assignment.objects.filter(topic=topic, topic__course__term=Term.get_active_term()):
        if assignment.open_places_in_slot_count < group.size:
            open_assignment_count -= 1
    return open_assignment_count


def all_applications_from_group(group_id, collection_number):
    """
    Returns all applications in the collection of the given group.
    :param group_id: the id of the group
    :param collection_number: the number of the collection to return the applications of
    :return: a list containing all applications in the given collection of the given group sorted by their priority
    """
    return list(TopicSelection.objects.filter(group_id=group_id, topic__course__term=Term.get_active_term()).filter(
        collection_number=collection_number).order_by(
        'priority'))


def get_all_applications_by_collection():
    """returns a dictionary with a (group,collection_number) pair as key, containing all applications for this group in
     this collection
    """

    application_for_group = {}
    for application in TopicSelection.objects.filter(topic__course__term=Term.get_active_term()):
        if (application.group, application.collection_number) not in application_for_group:
            application_for_group[(application.group, application.collection_number)] = []
        application_for_group[(application.group, application.collection_number)].append(application)
    return application_for_group


def get_all_applications_in_assignments():
    """returns a list of (group,collection_number) pairs, containing all accepted applications"""
    all_accepted_applications = []
    for assignment in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        for accepted_application in assignment.accepted_applications.all():
            all_accepted_applications.append((accepted_application.group, accepted_application.collection_number))
    return all_accepted_applications


def get_broken_slots():
    """
    returns two lists of all broken slots each with (topicID, slotid, String of the Slot, Error Message) Tuples.
    The first list are slots that are non-critical errors, and the second are slots that are critical errors and could
    cause issues
    """
    broken_slots = []
    critical_broken_slots = []
    for slot in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        try:
            slot.clean()
        except ValidationError as e:
            critical_broken_slots.append((slot.topic.id, slot.id, str(slot), str(e)))
        else:
            if not slot.assigned_student_to_slot_count == 0 and \
                    slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                broken_slots.append(
                    (slot.topic.id, slot.id, str(slot), "Less than minimal amount of student in this slot"))
    return broken_slots, critical_broken_slots


def get_max_score():
    """
    :return: Returns the highest possible score when considering the current applications
    :rtype: int
    """
    handled_applications = []
    score = 0
    for application in TopicSelection.objects.filter(Term.get_active_term()):
        if (application.group, application.collection_number) not in handled_applications:
            handled_applications.append((application.group, application.collection_number))
            score += get_score_for_assigned(1)
    return score


def get_score_for_assigned(priority):
    """
    Calculates the score if an application is assigned to a topic with the given priority

    :param priority: the priority to calculate the score for
    :return: the calculated score
    :rtype: int
    """
    return 21 - min(11, priority)


def get_score_for_not_assigned():
    """
    Calculates the score if an application is not assigned to any topic

    :return: the calculated score
    :rtype: int
        """
    return -30


def check_collection_satisfied(application):
    """returns if the collection the group from this application is satisfied or not"""
    return Assignment.objects.filter(accepted_applications__group=application.group,
                                     accepted_applications__collection_number=application.collection_number,
                                     topic__course__term=Term.get_active_term()).exists()


def get_group_data(group_id, collection_id):
    """
    :return: all the group data connected to the given collection of the given group
    :rtype: JsonResponse
    """
    group = Group.objects.get(id=group_id)

    members = []
    group_name = ""
    for member in group.members:
        members.append(member.tucan_id)

    assignment_query = Assignment.objects.filter(accepted_applications__group__in=[group],
                                                 accepted_applications__collection_number=collection_id)
    assigned = assignment_query.get().topic.id if assignment_query.exists() else None

    application_in_collection = []
    for application in all_applications_from_group(group_id, collection_id):
        topic = {
            'id': application.topic.id,
            'name': application.topic.title,
            'priority': application.priority,
            'freeSlots': possible_assignments_of_group_to_topic(application.topic, application.group)
        }
        application_in_collection.append(topic)

    return JsonResponse(
        {
            'selectedGroup': group_id,
            'selectedCollection': collection_id,
            'members': members,
            'assigned': assigned,
            'collection': application_in_collection
        }
    )
