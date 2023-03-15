from django.urls import path, include

from . import views

app_name = "backend"

urlpatterns = [
    path('assignment/', views.assignment_page, name='assignment_page'),
    path('home/', views.home_page, name='home_page'),
    path('export-applications-and-assignments/', views.export_applications_and_assignments_page,
         name='export_applications_and_assignments_page'),
    path('admin_functionality/', views.admin, name='admin_page'),
    path('term_finalized/',views.term_finalized, name='term_finalized'),
    # path('__debug__/', include('debug_toolbar.urls')),

]
