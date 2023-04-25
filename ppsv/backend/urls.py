from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [
    path('assignments/manual', views.assignment_page, name='manual'),
    path('assignments', views.overview, name='overview'),
    path('assignments/export', views.export_applications_and_assignments_page,
         name='export'),
    path('assignments/manage', views.control_flow, name='manage'),
    path('term_finalized/',views.term_finalized, name='term_finalized'),
    # path('__debug__/', include('debug_toolbar.urls')),
]
