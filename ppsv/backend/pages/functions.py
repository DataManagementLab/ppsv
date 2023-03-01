from django.core.exceptions import ValidationError
from django.http import JsonResponse

from backend.models import Assignment
from backend.models import get_score_for_assigned, get_score_for_not_assigned
from course.models import TopicSelection, Term


def handle_get_chart_data(request):
    """Creates the data for the assignment chart.

    :return: The data for the assignment chart.
    :rtype: JsonResponse
    """

    application_query, assignment_query = get_filtered_query_from_request(request)

    data = {
        'groups': {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            -1: 0
        },
        'students': {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            -1: 0
        }
    }

    accepted_application = []
    for assignment in assignment_query:
        for application in assignment.accepted_applications.all():
            if (application.group, application.collection_number) not in accepted_application:
                accepted_application.append((application.group, application.collection_number))
            if application.priority > 5:
                data['groups'][6] += 1
            else:
                data['groups'][application.priority] += 1
            data['students'][application.priority] += application.group.size

    for application in application_query:
        if (application.group, application.collection_number) not in accepted_application:
            accepted_application.append((application.group, application.collection_number))
            data['groups'][-1] += 1
            data['students'][-1] += application.group.size

    return JsonResponse(data={
        'groups': [i for i in data['groups'].values()],
        'students': [i for i in data['students'].values()]
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
    """returns a list of all broken slots with (topicID, String of the Slot, Error Message) Tuples"""
    broken_slots = 0
    for slot in assignment_query.all():
        try:
            slot.clean()
        except ValidationError as e:
            broken_slots += 1
        else:
            if not slot.assigned_student_to_slot_count == 0 and \
                    slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                broken_slots += 1

    return JsonResponse({
        "score": score,
        "maxScore": max_score,
        "brokenSlots": broken_slots,
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
