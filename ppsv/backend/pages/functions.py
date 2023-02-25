from django.http import JsonResponse

from backend.models import Assignment
from course.models import TopicSelection


def handle_get_chart_data(request):
    """Creates the data for the assignment chart.

    :return: The data for the assignment chart.
    :rtype: JsonResponse
    """
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
