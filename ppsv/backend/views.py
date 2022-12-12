from .pages.assignment_page import assignment_page
from .pages.home_page import home_page


# Create your views here.

def assignment_view(request):
    assignment_page(request)


def home_view(request):
    home_page(request)
