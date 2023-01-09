from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.automatic_assignment import main
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

def handle_do_automatic_assignments(request):
    main.main(True)
    return JsonResponse(
        {
            'status': "done"
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

    if action == "getChartData":
        return handle_get_chart_data()

    if action == "doAutomaticAssignments":
        return handle_do_automatic_assignments(request)

    raise ValueError(f"invalid request action: {action}")


def home_page(request):
    """The view for the home page.

    :param request: the given request send by the home html-page

    :return: a render() object
    :rtype: HttpResponse
    """
    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    if request.method == "POST":
        return handle_post(request)

    return render(request, 'backend/home.html')
