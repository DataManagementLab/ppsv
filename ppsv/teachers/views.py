from django.shortcuts import render

from teachers.pages.overview_page import overview_page


def overview(request):
    overview_page(request)