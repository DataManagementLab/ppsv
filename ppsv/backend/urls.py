from django.urls import path
from . import views

app_name = "backend"

urlpatterns = [
    path('assignment/', views.assignment_page, name='assignment_page'),
    path('home/', views.home_page, name='home_page'),
]
