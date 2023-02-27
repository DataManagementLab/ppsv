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
