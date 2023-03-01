from django.http import JsonResponse

from backend.pages.functions import get_filtered_query_from_request


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
