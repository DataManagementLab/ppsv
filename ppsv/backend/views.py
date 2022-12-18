import csv
import zipfile

from django.http import FileResponse, HttpResponse

from course.models import Topic
from backend.models import Assignment
from .admin import TopicSelectionResource
from .pages.assignment_page import assignment_page
from .pages.home_page import home_page
from .pages.export_applications_and_assignments_page import export_applications_and_assignments_page


# Create your views here.


def assignment_view(request):
    assignment_page(request)


def home_view(request):
    home_page(request)


def export_applications_and_assignments_view(request):
    export_applications_and_assignments_page(request)