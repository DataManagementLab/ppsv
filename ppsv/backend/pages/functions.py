from django.http import JsonResponse

from backend.models import Assignment
from course.models import TopicSelection


def handle_get_chart_data(request):
    """Creates the data for the assignment chart.

    :return: The data for the assignment chart.
    :rtype: JsonResponse
    """
    data = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        -1: 0
    }

    min_cp = int(request.POST.get('minCP'))
    max_cp = int(request.POST.get('maxCP'))
    course_types = request.POST.getlist('courseTypes[]')
    faculties = request.POST.getlist('faculties[]')
    assignment_priorities = {}

    if max_cp == -1:
        assignment_query = Assignment.objects.filter(topic__course__cp__gte=min_cp,
                                                     topic__course__type__in=course_types,
                                                     topic__course__faculty__in=faculties)
        application_query = TopicSelection.objects.filter(topic__course__cp__gte=min_cp,
                                                          topic__course__type__in=course_types,
                                                          topic__course__faculty__in=faculties)
    else:
        assignment_query = Assignment.objects.filter(topic__course__cp__range=(min_cp, max_cp),
                                                     topic__course__type__in=course_types,
                                                     topic__course__faculty__in=faculties)
        application_query = TopicSelection.objects.filter(topic__course__cp__range=(min_cp, max_cp),
                                                          topic__course__type__in=course_types,
                                                          topic__course__faculty__in=faculties)

    for assignment in assignment_query:
        for application in assignment.accepted_applications.all():
            assignment_priorities[(application.group.id, application.collection_number)] = application.priority

    for topic_selection in application_query:
        key = (topic_selection.group.id, topic_selection.collection_number)
        if key not in assignment_priorities:
            assignment_priorities[key] = -1

    for priority in assignment_priorities.values():
        if priority > 5:
            data[6] += 1
        else:
            data[priority] += 1

    return JsonResponse(data={
        'values': [i for i in data.values()]
    })
