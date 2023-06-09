from django.shortcuts import render

from .pages.admin_page import control_flow
from .pages.assignment_page import assignment_page
from .pages.home_page import overview
from .pages.export_applications_and_assignments_page import export_applications_and_assignments_page


# Create your views here.


def assignment_view(request):
    assignment_page(request)


def export_applications_and_assignments_view(request):
    export_applications_and_assignments_page(request)


def term_finalized(request):
    return render(request, 'backend/term_finalized.html')
