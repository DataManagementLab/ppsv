from django.http import HttpResponse
from django.shortcuts import render


def selection_page(request):
    return render(request, 'frontend/selection_page.html')