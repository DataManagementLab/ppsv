import csv
import traceback

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from backend.automatic_assignment import main
from backend.import_data.applications import *
from backend.import_data.assignments import *
from backend.models import Assignment, TopicSelection
from backend.models import TermFinalization
from backend.pages.functions import get_broken_slots, get_or_error, get_score_and_chart_data
from course.models import Course, CourseType, Term
from ppsv import settings


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
    all_applications_in_assignments = AcceptedApplications.get_collection_dict()
    for collection in TopicSelection.get_collection_dict():
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


def handle_import(request):
    """Imports the given file to the database, keeps all currently locked slots and locked assigned applications as they
    are, but overrides all remaining assigned applications. Only the assigned applications of the faculties that are
    imported get changed.

    :param request: the request containing the csv file to import

    :return: a JsonResponse containing a success status (true if import worked, false otherwise), a message with a
    detailed description and possibly an error list, containing all errors that occurred while trying to import
    :rtype: JsonResponse
    """
    uploaded_file = request.FILES.get('document')

    if uploaded_file is None:
        return JsonResponse(data={
            'successStatus': False,
            'msg': 'There was no file selected.',
            'errorList': [],
        })

    if not uploaded_file.content_type == 'text/csv':
        return JsonResponse(data={
            'successStatus': False,
            'msg': 'The file type was not "csv".',
            'errorList': [],
        })

    if TermFinalization.is_finalized(Term.get_active_term()):
        return JsonResponse(data={
            'successStatus': False,
            'msg': 'The term is already finalized.',
            'errorList': [],
        })

    name_of_saved_file = 'imported_file.csv'
    fs = FileSystemStorage(location='import_export_tmp/')
    content = uploaded_file.read()
    file_content = ContentFile(content)
    if fs.exists(name_of_saved_file):
        fs.delete(name_of_saved_file)
    file_name = fs.save(name_of_saved_file, file_content)
    tmp_file = fs.path(file_name)
    csv_file = open(tmp_file, errors='ignore')
    delimiter_char = ','
    reader = csv.reader(csv_file, delimiter=delimiter_char)

    for row in reader:
        if ';' in row[0]:
            delimiter_char = ';'
        break

    with open(tmp_file, errors='ignore') as imported_file:
        imported_file_reader = csv.reader(imported_file, delimiter=delimiter_char)

        init_assignments(True)
        init_applications(True)

        assignments = Assignments()
        applications = Applications()

        # list of ('row-number', 'row-content', 'ERROR string')
        error_list = []

        imported_faculties = []
        row_count = 1
        for row in imported_file_reader:
            if row_count != 1:
                if len(row) != 4:
                    error_list.append([row_count, row, 'The row seems corrupted in a strange way'])
                    continue
                try:
                    topic_id = int(row[0])
                except:
                    error_list.append([row_count, row, 'The topic ID (' + row[0] + ') is not a valid number'])
                    continue

                try:
                    slot_id = int(row[1])
                except:
                    error_list.append([row_count, row, 'The slot ID (' + row[1] + ') is not a valid number'])
                    continue

                assignees = row[3]

                if not Topic.objects.filter(id=topic_id).exists():
                    error_list.append([row_count, row, 'Topic (' + row[0] + ') does not exist.'])
                    continue

                topic = Topic.objects.get(id=topic_id)

                if not (topic.course.term.id == Term.get_active_term().id):
                    error_list.append([row_count, row, 'Topic (' + row[0] + ') does not exist in current term.'])

                if not (topic.course.faculty in imported_faculties):
                    imported_faculties.append(topic.course.faculty)

                for application in assignees.split(','):
                    if application != '':
                        try:
                            application_id = int(application)
                        except:
                            error_list.append(
                                [row_count, row, '"' + application + '" is not a valid number for an application'])
                            continue

                        # application exists
                        if TopicSelection.objects.filter(id=application_id).exists():
                            if TopicSelection.objects.get(id=application_id).topic.id != topic_id:
                                error_list.append(
                                    [row_count, row,
                                     'The application (' + application + ') does not match the Topic (' + row[0] + ')'])
                            else:
                                # test if applicaton locke or in locked slot
                                if applications.application_locked(application_id):
                                    error_list.append([row_count, row,
                                                       'The application (' + application + ') or the slot it is currently in, is locked.'])
                                else:
                                    assignment_worked, msg = assignments.add_application(
                                        applications.get_application(application_id), slot_id)
                                    if not assignment_worked:
                                        error_list.append([row_count, row, msg])
                        else:
                            error_list.append([row_count, row, 'The application (' + application + ') does not exist'])

            row_count += 1

    if len(error_list) != 0:
        return JsonResponse(data={
            'successStatus': False,
            'msg': 'Some errors occurred and import could not be saved.',
            'errorList': error_list,
        })

    assignments.save_to_database(Term.get_active_term(), imported_faculties)

    return JsonResponse(data={
        'successStatus': True,
        'msg': 'Data imported.',
        'errorList': [],
    })


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
        if action == "import":
            return handle_import(request)

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took "
                                    f"to get this message to an administrator!")

    except Exception as e:
        if settings.DEBUG:
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

    # --- STATISTIC TERM --- #
    active_term = Term.get_active_term()

    terms = []
    for term in Term.objects.all():
        if term == active_term:
            terms.append((str(term) + "(active)", term.id))
        else:
            terms.append((term, term.id))

    args["terms"] = terms
    args["active"] = active_term



    return render(request, 'backend/home.html', args)
