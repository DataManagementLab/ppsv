import csv
import zipfile

from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect
from django.urls import reverse

from backend.models import Assignment
from course.models import Topic, TopicSelection


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

    #variables
    faculty = request.GET.get('faculty')
    print(faculty)

    # the export_applications csv file is created manually by accessing the database, fetching the required data and
    # saved for being added to the zip archive later
    applications_response = HttpResponse(content_type='text/csv')

    application_writer = csv.writer(applications_response)
    application_writer.writerow(
        ['ApplicationID', 'TopicID', 'topic name', 'GroupID', 'group size', 'collection number', 'priority'])

    for application in TopicSelection.objects.all():
        if 'all' == faculty or application.topic.course.faculty == faculty:
            application_writer.writerow(
                [application.id, application.topic.id, application.topic.title, application.group.id,
                 application.group.size, application.collection_number, application.priority])

    applications_response['Content-Disposition'] = 'attachment; filename=export_applications_file'

    applications_file_for_temporary_use = open(export_applications_file, "wb")
    applications_file_for_temporary_use.write(applications_response.content)

    applications_file_for_temporary_use.close()

    # the export_assignments csv file is created manually by accessing the database, fetching the required data and
    # saved for being added to the zip archive later
    assignments_response = HttpResponse(content_type='text/csv')

    assignment_writer = csv.writer(assignments_response)
    assignment_writer.writerow(['TopicID', 'SlotID', 'Slot size', 'assignees'])

    for topic in Topic.objects.all():
        if 'all' == faculty or topic.course.faculty == faculty:
            for slot_id in range(1, topic.max_slots + 1):
                assignees = ''
                slotSize = '%d~%d' % (topic.min_slot_size, topic.max_slot_size)

                if Assignment.objects.all().filter(topic__id=topic.id).filter(slot_id=slot_id).exists():
                    for assignment in Assignment.objects.all().filter(topic__id=topic.id).filter(
                            slot_id=slot_id).get().accepted_applications.all():
                        assignees = assignees + '%s,' % assignment.id

                assignment_writer.writerow([topic.id, slot_id, slotSize, assignees])

    assignments_response['Content-Disposition'] = 'attachment; filename=export_assignments_file'

    assignments_file_for_temporary_use = open(export_assignments_file, "wb")
    assignments_file_for_temporary_use.write(assignments_response.content)

    assignments_file_for_temporary_use.close()

    # creates the zip file and adds the created csv files to be exported
    zip_file_to_export = zipfile.ZipFile(export_applications_and_assignments_file, 'w')
    zip_file_to_export.write(export_applications_file)
    zip_file_to_export.write(export_assignments_file)

    return FileResponse(open(export_applications_and_assignments_file, 'rb'), as_attachment=True)
