import csv
import zipfile

from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect
from django.urls import reverse

from backend.admin import TopicSelectionResource
from backend.models import Assignment
from course.models import Topic


def export_applications_and_assignments_page(request):
    """The view for the export_applications_and_assignments page.

    :param request: the given request send by the export_applications_and_assignments html-page
        In case of the request specifying a user who is not allowed to access this download-page redirects to the
        login page.

    :return: a zip-archive containing the applications and assignments .csv files
    :rtype: FileResponse
    """
    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    # the export_applications csv file is created by using the corresponding resource model and saved for being added to
    # the zip archive later
    applicationsDataset = TopicSelectionResource().export()
    applicationsFileForTemporaryUse = open("export_applications.csv", "w")
    applicationsFileForTemporaryUse.write(applicationsDataset.csv)
    applicationsFileForTemporaryUse.close()

    # the export_assignments csv file is created manually by accessing the database, fetching the required data and
    # saved for being added to the zip archive later
    assignmentsResponse = HttpResponse(content_type='text/csv')

    assignmentWriter = csv.writer(assignmentsResponse)
    assignmentWriter.writerow(['TopicID', 'SlotID', 'CourseID(course name)', 'Slot size', 'assignees'])

    for topic in Topic.objects.all():
        for slotID in range(topic.max_slots):
            assignees = ''
            course = '%d(%s)' % (topic.course.id, topic.course.title)
            slotSize = '%d-%d' % (topic.min_slot_size, topic.max_slot_size)

            if Assignment.objects.all().filter(topic__id=topic.id).filter(slot_id=slotID).count():
                for assignment in Assignment.objects.all().filter(topic__id=topic.id).filter(
                        slot_id=slotID).get().accepted_applications.all():
                    assignees = assignees + '%s,' % assignment.id

            assignmentWriter.writerow([topic.id, slotID, course, slotSize, assignees])

    assignmentsResponse['Content-Disposition'] = 'attachment; filename="export_assignments.csv"'

    assignmentsFileForTemporaryUse = open("export_assignments.csv", "wb")
    assignmentsFileForTemporaryUse.write(assignmentsResponse.content)

    assignmentsFileForTemporaryUse.close()

    # creates the zip file and adds the created csv files to be exported
    zipFileToExport = zipfile.ZipFile('export_applications_and_assignments.zip', 'w')
    zipFileToExport.write('export_applications.csv')
    zipFileToExport.write('export_assignments.csv')

    return FileResponse(open('export_applications_and_assignments.zip', 'rb'), as_attachment=True)