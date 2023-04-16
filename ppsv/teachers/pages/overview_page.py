import traceback

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from backend.models import TopicSelection, AcceptedApplications
from backend.pages.functions import get_or_none
from base.models import CourseType, Course, Topic, Term
from ppsv import settings
from teachers.pages.functions import get_or_error


def handle_create_course(request):
    """
    Handles the creation of a new course specified by the user

    :return: If the creation was a success
    :rtype: JsonResponse
    """
    course_title = request.POST.get("course_title")
    course_type = request.POST.get("course_type")
    course_faculty = request.POST.get("course_faculty")
    course_term = request.POST.get("course_term_id")
    course_registration_start_date = request.POST.get("course_registration_start_date")
    course_registration_start_time = request.POST.get("course_registration_start_time")
    course_registration_start = parse_datetime(course_registration_start_date + " " + course_registration_start_time)
    course_registration_start = make_aware(course_registration_start)
    course_registration_end_date = request.POST.get("course_registration_end_date")
    course_registration_end_time = request.POST.get("course_registration_end_time")
    course_registration_end = parse_datetime(course_registration_end_date + " " + course_registration_end_time)
    course_registration_end = make_aware(course_registration_end)
    course_cp = request.POST.get("course_cp")
    if request.POST.get("course_motivational_text") == 'on':
        course_motivational_text = True
    else:
        course_motivational_text = False
    course_description = request.POST.get("course_description")

    if course_registration_start >= course_registration_end:
        return JsonResponse(
            {
                "status": "error",
                "message": "registration start must be before registration end!",
            }
        )

    if course_term == "":
        return JsonResponse(
            {
                "status": "error",
                "message": "There is no term active. Please contact an Administrator."
            }
        )

    Course.objects.create(title=course_title, type_id=course_type, faculty=course_faculty, term_id=course_term,
                          registration_start=course_registration_start,
                          registration_deadline=course_registration_end, description=course_description,
                          cp=course_cp, created_by=request.user, motivation_text=course_motivational_text)

    return JsonResponse(
        {
            "status": "success"
        }
    )


def handle_create_topic(request):
    """
    Handles the creation of a new topic specified by the user

    :return: If the creation was a success
    :rtype: JsonResponse
    """
    topic_title = request.POST.get("topic_title")
    topic_course = request.POST.get("topic_course")
    topic_max_slots = request.POST.get("topic_max_slots")
    topic_min_size = request.POST.get("topic_min_size")
    topic_max_size = request.POST.get("topic_max_size")
    topic_description = request.POST.get("topic_description")
    topic_file = request.FILES.get("topic_file")

    course = get_or_error(Course, pk=topic_course)

    if course.term.active_term is not True:
        return JsonResponse({
            "status": "error",
            "message": "The selected course is not in an active term"
        })

    Topic.objects.create(title=topic_title, course_id=topic_course, max_slots=topic_max_slots,
                         min_slot_size=topic_min_size, max_slot_size=topic_max_size, description=topic_description,
                         file=topic_file)

    return JsonResponse(
        {
            "status": "success"
        }
    )


def handle_edit_course(request):
    """
    Handles the editing of a course to new specifications from the user

    :return: If the edit was a success
    :rtype: JsonResponse
    """
    course_id = request.POST.get("course_id")
    course_title = request.POST.get("course_title")
    course_type = request.POST.get("course_type")
    course_faculty = request.POST.get("course_faculty")
    course_registration_start_date = request.POST.get("course_registration_start_date")
    course_registration_start_time = request.POST.get("course_registration_start_time")
    course_registration_start = parse_datetime(course_registration_start_date + " " + course_registration_start_time)
    course_registration_start = make_aware(course_registration_start)
    course_registration_end_date = request.POST.get("course_registration_end_date")
    course_registration_end_time = request.POST.get("course_registration_end_time")
    course_registration_end = parse_datetime(course_registration_end_date + " " + course_registration_end_time)
    course_registration_end = make_aware(course_registration_end)
    course_cp = request.POST.get("course_cp")
    if request.POST.get("course_motivational_text") == 'on':
        course_motivational_text = True
    else:
        course_motivational_text = False
    course_description = request.POST.get("course_description")

    if course_registration_start >= course_registration_end:
        return JsonResponse(
            {
                "status": "error",
                "message": "registration start must be before registration end!",
            }
        )

    course = get_or_error(Course, pk=course_id)
    course.title = course_title
    course.type = get_or_error(CourseType, pk=course_type)
    course.faculty = course_faculty
    course.registration_start = course_registration_start
    course.registration_deadline = course_registration_end
    course.cp = course_cp
    course.motivation_text = course_motivational_text
    course.description = course_description
    course.save()

    return JsonResponse({
        "status": "success"
    })


def handle_edit_topic(request):
    """
    Handles the editing of a topic to new specifications from the user

    :return: If the edit was a success
    :rtype: JsonResponse
    """
    topic_id = request.POST.get("topic_id")
    topic_title = request.POST.get("topic_title")
    topic_course = request.POST.get("topic_course")
    topic_max_slots = request.POST.get("topic_max_slots")
    topic_min_size = request.POST.get("topic_min_size")
    topic_max_size = request.POST.get("topic_max_size")
    topic_description = request.POST.get("topic_description")
    topic_file = request.FILES.get("topic_file")

    course = get_or_error(Course, pk=topic_course)

    topic = get_or_error(Topic, pk=topic_id)

    if topic.course.term.active_term is not True:
        return JsonResponse({
            "status": "error",
            "message": "The current term is in an not active term"
        })

    if course.term.active_term is not True:
        return JsonResponse({
            "status": "error",
            "message": "The selected course is not in an active term"
        })

    topic.title = topic_title
    topic.course = course
    topic.max_slots = topic_max_slots
    topic.min_slot_size = topic_min_size
    topic.max_slot_size = topic_max_size
    topic.description = topic_description
    if topic_file is not None:
        topic.file = topic_file
    topic.save()

    return JsonResponse({
        "status": "success"
    })


def handle_bulk_courses(request):
    """
    Handles the request for all courses and their topics

    :return: All courses and topics created by the user
    :rtype: JsonResponse
    """
    temp_course_list = []
    topics_of_courses = []
    topics = []
    last_course = ""
    if Topic.objects.exists():
        for topic in Topic.objects.filter(course__created_by=request.user):
            if topic.course.title not in temp_course_list:
                temp_course_list.append(topic.course.title)
            if last_course != topic.course.title:
                last_course = topic.course.title
                topics = []
                topics_of_course = {"id": topic.course.pk, "title": topic.course.title, "topics": topics,
                                    "type": topic.course.type.type, "typeID": topic.course.type.pk,
                                    "faculty": topic.course.faculty,
                                    "term": topic.course.term.name, "term_active": topic.course.term.active_term,
                                    "startdate": topic.course.registration_start,
                                    "enddate": topic.course.registration_deadline, "cp": topic.course.cp,
                                    "motText": topic.course.motivation_text, "description": topic.course.description}
                topics_of_courses.append(topics_of_course)
            file_url = ""
            if topic.file:
                file_url = topic.file.url
            topics.append(
                {"id": topic.pk, "title": topic.title, "description": topic.description, "nrSlots": topic.max_slots,
                 "minGroupSize": topic.min_slot_size, "maxGroupSize": topic.max_slot_size, "file": file_url})

    if Course.objects.exists():
        for course in Course.objects.filter(~Q(title__in=temp_course_list), created_by=request.user):
            topics_of_courses.append({"id": course.pk, "title": course.title, "topics": [],
                                      "type": course.type.type, "typeID": course.type.pk, "faculty": course.faculty,
                                      "term": course.term.name, "term_active": course.term.active_term,
                                      "startdate": course.registration_start,
                                      "enddate": course.registration_deadline, "cp": course.cp,
                                      "motText": course.motivation_text, "description": course.description})

    return JsonResponse(
        {
            "courses": topics_of_courses
        }
    )


def handle_select_topic(request):
    """
    Handles the selection of a topic
    @param request: the information about the associated topic
    @return: the necessary information about the applications and assignment
    """

    # get topic
    topic = get_or_error(Topic, id=int(request.POST.get("topicID")))

    # get query applications for topic
    applications = TopicSelection.objects.filter(topic=topic, topic__course__term=Term.get_active_term())

    slots = []
    unassigned_groups = []

    # get information for every slot of the topic
    for slot in range(1, topic.max_slots + 1):
        data = {
            'slotID': slot,
        }

        groups = []
        student_count = 0
        for application in applications:
            accepted_application = get_or_none(AcceptedApplications,
                                               assignment__topic=topic,
                                               assignment__topic__course__term=Term.get_active_term(),
                                               topic_selection=application)

            # check if the application is assigned to the current slot
            if accepted_application is not None and accepted_application.assignment.slot_id == slot:
                groups.append(list(map(lambda x: x.firstname + " " + x.lastname + " &lt" + x.email + "&gt",
                                       application.group.members)))
                student_count += application.group.members.count()

            # check if the application is not assigned to any slot (could be improved performance-wise)
            elif accepted_application is None:
                unassigned_group = list(
                    map(lambda x: x.firstname + " " + x.lastname + " &lt" + x.email + "&gt", application.group.members))

                # check if the group is already in the list of unassigned groups to avoid duplicates
                if unassigned_group not in unassigned_groups:
                    unassigned_groups.append(unassigned_group)

        data['groups'] = groups
        data['studentCount'] = student_count

        slots.append(data)

    return JsonResponse(
        {
            'topicMinSlotSize': topic.min_slot_size,
            'topicMaxSlotSize': topic.max_slot_size,
            'slots': slots,
            'unassignedGroups': unassigned_groups,
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

        if action == "createCourse":
            return handle_create_course(request)
        if action == "createTopic":
            return handle_create_topic(request)
        if action == "editCourse":
            return handle_edit_course(request)
        if action == "editTopic":
            return handle_edit_topic(request)
        if action == "getBulkCourses":
            return handle_bulk_courses(request)
        if action == "selectTopic":
            return handle_select_topic(request)

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took "
                                    f"to get this message to an administrator!")

    except Exception as e:
        if settings.DEBUG:
            print(traceback.format_exc())
        return HttpResponse(status=500, content=f"request {action} caused an exception: \n {e}")


def overview_page(request):
    """The view for the teacher overview page.

    :param request: the given request send by the home html-page

    :return: a render() object
    :rtype: HttpResponse
    """
    if not request.user.is_staff and not request.user.groups.filter(name="teacher").exists():
        return redirect(reverse('frontend:login') + '?next=' + reverse('teachers:overview_page'))

    if request.method == "POST":
        return handle_post(request)

    args = {}

    topics_of_courses = []
    topics = []
    last_course = ""
    if Topic.objects.exists():
        for topic in Topic.objects.filter(course__created_by=request.user, course__term__active_term=True):
            if last_course != topic.course.title:
                last_course = topic.course.title
                topics = []
                topics_of_course = {"course": topic.course, "topics": topics}
                topics_of_courses.append(topics_of_course)
            topics.append(topic)

    if Course.objects.exists():
        for course in Course.objects.filter(~Q(title__in=topics_of_courses), created_by=request.user):
            topics_of_courses.append({"course": course, "topics": []})

    active_term = get_or_none(Term, active_term=True)

    course_types = []
    for course_type in CourseType.objects.all():
        course_types.append(course_type)

    faculties = []
    for faculty in Course.COURSE_FACULTY_CHOICES:
        faculties.append(faculty)
    faculties.sort()

    args["topics_of_courses"] = topics_of_courses
    args["active_term"] = active_term
    if active_term is not None:
        args["active_term_reg_start_date"] = active_term.registration_start.strftime("%Y-%m-%d")
        args["active_term_reg_start_time"] = active_term.registration_start.strftime("%H:%S")
        args["active_term_reg_end_date"] = active_term.registration_deadline.strftime("%Y-%m-%d")
        args["active_term_reg_end_time"] = active_term.registration_deadline.strftime("%H:%S")
    args["course_types"] = course_types
    args["faculties"] = faculties

    return render(request, 'teachers/overview.html', args)
