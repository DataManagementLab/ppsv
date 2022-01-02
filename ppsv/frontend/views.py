from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView


def homepage(request):
    template_name = 'frontend/homepage.html'

    args = {}
    return render(request, template_name, args)


def selection(request):
    template_name = 'frontend/selection.html'
    courses = models.Course.objects.all()
    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'

    # faculties contains all distinct faculties
    faculties = models.Course.objects.order_by().values('faculty').distinct()
    # topics contains all topics
    topics = models.Topic.objects.all()
    topic_choices = []

    chosen_faculty = ""

    if request.method == "POST":

        for i in range(len(faculties)):

            if faculties[i]['faculty'] in request.POST:
                # When a form is send by the POST method the chosen faculty will be set to the chosen faculty
                chosen_faculty = faculties[i]['faculty']
                print(chosen_faculty)

    # Courses which are from the chosen faculty
    courses = models.Course.objects.filter(faculty=chosen_faculty)

    # Topics which are in the chosen courses
    for selected_course in courses:
        topic_choices.append(models.Topic.objects.filter(course=selected_course))

    args = {'courses': courses, "topicChoices": topic_choices, "faculties": faculties}
    return render(request, template_name, args)


def groups(request):
    template_name = 'frontend/groups.html'
    args = {}
    return render(request, template_name, args)


def login(request):
    template_name = 'frontend/login.html'
    return render(request, template_name)
