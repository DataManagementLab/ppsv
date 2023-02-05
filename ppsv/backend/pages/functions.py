from django.http import JsonResponse

from backend.models import Assignment
from course.models import TopicSelection


def handle_get_chart_data():
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

    assignment_priorities = {}

    for assignment in Assignment.objects.all():
        for application in assignment.accepted_applications.all():
            key = (application.group.id, application.collection_number)
            if key not in assignment_priorities:
                assignment_priorities[key] = application.priority
            else:
                assignment_priorities[key] = min(assignment_priorities[key], application.priority)

    for topic_selection in TopicSelection.objects.all():
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