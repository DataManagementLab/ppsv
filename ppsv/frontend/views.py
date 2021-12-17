from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView
from frontend.forms.forms import ContactForm
from frontend.forms.forms import FacultyForm


def homepage(request):
    template_name = 'frontend/homepage.html'

    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            print(name, email)

    args = {'form': form}
    return render(request, template_name, args)


def selection(request):
    template_name = 'frontend/selection.html'
    courses = models.Course.objects.all()
    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'

    faculties = models.Course.objects.order_by().values('faculty').distinct()

    chosen_faculty = ""

    form = FacultyForm()
    if request.method == "POST":
        form = FacultyForm(request.POST)

        for i in range(len(faculties)):

            if faculties[i]['faculty'] in request.POST:
                chosen_faculty = faculties[i]['faculty']

    courses = models.Course.objects.filter(faculty=chosen_faculty)

    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics, "faculties": faculties}
    return render(request, template_name, args)


def groups(request):
    template_name = 'frontend/groups.html'
    args = {}
    return render(request, template_name, args)


def login(request):
    template_name = 'frontend/login.html'
    return render(request, template_name)
