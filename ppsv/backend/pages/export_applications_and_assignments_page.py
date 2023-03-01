import csv
import zipfile

from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect
from django.urls import reverse

from backend.models import Assignment, AcceptedApplications
from course.models import Topic, TopicSelection, Term


def write_row_assignment_helper(topic, slot_id, assignment_writer):
    """A method to help writing the data of an assignment to the corresponding file, if the conditions are met.
    Assignments are not added if either the slot belonging to them is not finalized, or all applications assigned to the
    assignment are not only finalized but also add up to the maximum size of the assignment.

        :param topic: the topic of which the data should be added
        :type topic: Topic object
        :param slot_id: the slotID of the assignment
        :type slot_id: int
        :param assignment_writer: the writer writing the assignment data to the file
        :type assignment_writer: csv writer
        """
    assignees = ''
    min_size = topic.min_slot_size
    max_size = topic.max_slot_size

    if Assignment.objects.all().filter(topic__id=topic.id, slot_id=slot_id,
                                       topic__course__term=Term.get_active_term()).exists():
        for assigned_applications in Assignment.objects.all().filter(topic__id=topic.id,
                                                                     slot_id=slot_id,
                                                                     topic__course__term=Term.get_active_term()).get().accepted_applications.all():
            if not AcceptedApplications.objects.get(topic_selection=assigned_applications,
                                                    assignment=Assignment.objects.get(topic=topic.id,
                                                                                      slot_id=slot_id)).finalized_assignment:
                assignees = assignees + '%s,' % assigned_applications.id
            else:
                min_size -= assigned_applications.group.size
                max_size -= assigned_applications.group.size

    slotSize = '%d~%d' % (max(min_size, 0), max_size)
    if max_size > 0:
        assignment_writer.writerow([topic.id, slot_id, slotSize, assignees])


def write_row_application_helper(application, application_writer):
    """A method to help writing the data of an application to the corresponding file, if the conditions are met.
    Applications are added if in their corresponding collection no applications is either assigned and finalized,
    or assigned to a slot that is finalized.

    :param application: the application of which the data should be added
    :type application: a TopicSelection object
    :param application_writer: the writer writing the application data to the file
    :type application_writer: csv writer
    """
    not_add_application = False
    applications_in_collection = TopicSelection.objects.all().filter(group=application.group.id,
                                                                     collection_number=application.collection_number,
                                                                     topic__course__term=Term.get_active_term())

    if AcceptedApplications.objects.filter(topic_selection__in=applications_in_collection).all().exists():
        accepted_application = AcceptedApplications.objects.get(topic_selection__in=applications_in_collection)
        not_add_application = not_add_application or accepted_application.finalized_assignment
        not_add_application = not_add_application or accepted_application.assignment.finalized_slot

    if not not_add_application:
        application_writer.writerow(
            [application.id, application.topic.id, application.topic.title, application.group.id,
             application.group.size, application.collection_number, application.priority])


def export_applications_and_assignments_page(request):
    """The view for the export_applications_and_assignments page.

    :param request: the given request send by the export_applications_and_assignments html-page
        In case of the request specifying a user who is not allowed to access this download-page redirects to the
        home page.

    :return: a zip-archive containing the applications and assignments .csv files
    :rtype: FileResponse
    """

    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    # files
    export_applications_file = "export_applications.csv"
    export_assignments_file = "export_assignments.csv"
    export_applications_and_assignments_file = "export_applications_and_assignments.zip"

    # variables
    faculty = request.GET.get('faculty')

    # the export_applications csv file is created manually by accessing the database, fetching the required data and
    # saved for being added to the zip archive later
    applications_response = HttpResponse(content_type='text/csv')

    application_writer = csv.writer(applications_response)
    application_writer.writerow(
        ['ApplicationID', 'TopicID', 'topic name', 'GroupID', 'group size', 'collection number', 'priority'])

    for application in TopicSelection.objects.all():
        if 'all' == faculty or application.topic.course.faculty == faculty:
            write_row_application_helper(application, application_writer)

    applications_response['Content-Disposition'] = 'attachment; filename=export_applications_file'

    applications_file_for_temporary_use = open(export_applications_file, "wb")
    applications_file_for_temporary_use.write(applications_response.content)

    applications_file_for_temporary_use.close()

    # the export_assignments csv file is created manually by accessing the database, fetching the required data and
    # saved for being added to the zip archive later
    assignments_response = HttpResponse(content_type='text/csv')

    assignment_writer = csv.writer(assignments_response)
    assignment_writer.writerow(['TopicID', 'SlotID', 'Slot size', 'assignees'])

    for topic in Topic.objects.filter(course__term=Term.get_active_term()):
        if 'all' == faculty or topic.course.faculty == faculty:
            for slot_id in range(1, topic.max_slots + 1):
                assignment_exists = Assignment.objects.filter(topic=topic.id, slot_id=slot_id,
                                                              topic__course__term=Term.get_active_term()).exists()
                if not assignment_exists or (assignment_exists and not Assignment.objects.get(topic=topic.id,
                                                                                              slot_id=slot_id,
                                                                                              topic__course__term=Term.get_active_term()).finalized_slot):
                    write_row_assignment_helper(topic, slot_id, assignment_writer)

    assignments_response['Content-Disposition'] = 'attachment; filename=export_assignments_file'

    assignments_file_for_temporary_use = open(export_assignments_file, "wb")
    assignments_file_for_temporary_use.write(assignments_response.content)

    assignments_file_for_temporary_use.close()

    # creates the zip file and adds the created csv files to be exported
    zip_file_to_export = zipfile.ZipFile(export_applications_and_assignments_file, 'w')
    zip_file_to_export.write(export_applications_file)
    zip_file_to_export.write(export_assignments_file)

    return FileResponse(open(export_applications_and_assignments_file, 'rb'), as_attachment=True)
