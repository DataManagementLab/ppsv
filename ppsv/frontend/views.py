from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView


def selection_page(request):
    template_name = 'frontend/selection_page.html'
    courses = models.Course.objects.all()
    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics}
    return render(request, template_name, args)
