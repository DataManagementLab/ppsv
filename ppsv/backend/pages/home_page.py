from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.automatic_assignment import main
from backend.models import Assignment, get_all_applications_by_collection, get_all_applications_in_assignments
from course.models import TopicSelection, Course


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


def handle_do_automatic_assignments():
    main.main(True)
    return JsonResponse(
        {
            'status': "done"
        })


def handle_get_problems_listing():
    broken_slots = []
    for slot in Assignment.objects.all():
        try:
            slot.clean()
        except ValidationError as e:
            broken_slots.append((slot.topic.id, str(e)))
        else:
            if not slot.assigned_student_to_slot_count == 0 and \
                    slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                broken_slots.append(
                    (slot.topic.id, str(slot), "Less than minimal amount of student in this slot"))

    unfulfilled_collections = []
    all_applications_in_assignments = get_all_applications_in_assignments()
    for collection in get_all_applications_by_collection():
        if collection not in all_applications_in_assignments:
            unfulfilled_collections.append((str(collection[0]), collection[1], collection[0].id))

    return JsonResponse(
        data={
            'brokenSlots': broken_slots,
            'unfulfilledCollections': unfulfilled_collections,
        }
    )
    pass


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

    if action == "getProblemsListing":
        return handle_get_problems_listing()

    if action == "doAutomaticAssignments":
        return handle_do_automatic_assignments()

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

    args = {}

    # --- EXPORT --- #

    faculties = []
    for course in Course.objects.all():
        if course.faculty not in faculties:
            faculties.append(course.faculty)
    faculties.sort()

    args["faculties"] = faculties

    return render(request, 'backend/home.html', args)
