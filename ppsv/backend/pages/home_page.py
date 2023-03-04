import traceback

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.automatic_assignment import main
from backend.models import Assignment
from backend.pages.functions import get_all_applications_by_collection, \
    get_all_applications_in_assignments, get_broken_slots, get_or_error, get_score_and_chart_data
from course.models import Course, CourseType, Term


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


def handle_get_chart_data(request):
    """Creates the data for the assignment chart.

    :return: The data for the assignment chart.
    :rtype: JsonResponse
    """
    data = get_score_and_chart_data(request)
    return JsonResponse(data={
        'groups': data[0],
        'students': data[1],
        'score': data[2],
    })


def handle_clear_slot(request):
    """Clears the given slot"""
    slot = get_or_error(Assignment,
                        id=request.POST.get("assignmentID"),
                        topic__course__term=Term.get_active_term())
    slot.accepted_applications.clear()
    slot.delete()
    return HttpResponse(status=200)


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request
    """

    action = ""

    try:
        if "action" not in request.POST:
            return HttpResponse(status=501,
                                content="POST request didn't specify an action. Please report this and the actions "
                                        "you took to get this message to the administrator!")

        action = request.POST.get("action")

        if action == "getChartData":
            return handle_get_chart_data(request)
        if action == "getProblemsListing":
            return handle_get_problems_listing()
        if action == "doAutomaticAssignments":
            return handle_do_automatic_assignments()
        if action == "clearSlot":
            return handle_clear_slot(request)

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took "
                                    f"to get this message to an administrator!")

    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse(status=500, content=f"request {action} caused an exception: \n {e}")


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
