from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


def index(request):
    return HttpResponse(_("Hello, world. You're at the course view."))
