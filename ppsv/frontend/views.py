from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView


def selection(request):
    template_name = 'frontend/selection.html'
    courses = models.Course.objects.all()
    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics}
    return render(request, template_name, args)


def homepage(request):
    template_name = 'frontend/homepage.html'
    args = {}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'
    args = {}
    return render(request, template_name, args)


def groups(request):
    template_name = 'frontend/groups.html'
    args = {}
    return render(request, template_name, args)
