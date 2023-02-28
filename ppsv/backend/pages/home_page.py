from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.automatic_assignment import main
from backend.models import get_all_applications_by_collection, get_all_applications_in_assignments
from backend.models import get_broken_slots
from backend.pages.functions import handle_get_chart_data
from course.models import Course, CourseType


def handle_do_automatic_assignments():
    """
    Executes the automatic assignment

    :return: If the automatic assignment finished successful, returns a JSONResponse containing "status": "done"
    :rtype: JsonResponse
    """
    main.main(True)
    return JsonResponse(
        {
            'status': "done"
        })


def handle_get_problems_listing():
    """
    Creates a list of all slots with errors and an additional list on for all collections that are not fulfilled

    :return: a JsonResponse containing both lists
    :rtype: JsonResponse
    """
    unfulfilled_collections = []
    all_applications_in_assignments = get_all_applications_in_assignments()
    for collection in get_all_applications_by_collection():
        if collection not in all_applications_in_assignments:
            unfulfilled_collections.append((str(collection[0]), collection[1], collection[0].id))

    return JsonResponse(
        data={
            'brokenSlots': get_broken_slots(),
            'unfulfilledCollections': unfulfilled_collections,
        }
    )


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
        return handle_get_chart_data(request)

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

    course_types = []
    for course_type in CourseType.objects.all():
        course_types.append(course_type)

    # --- EXPORT --- #

    faculties = []
    for course in Course.objects.all():
        if course.faculty not in faculties:
            faculties.append(course.faculty)
    faculties.sort()

    args["course_types"] = course_types
    args["faculties"] = faculties
    args["range"] = range(1, 11)

    return render(request, 'backend/home.html', args)
