from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path('teachers/', views.CoursesOverview.as_view(), name='overview_page'),
    path('teachers/courses/add', views.AddCourseView.as_view(), name="course-add"),
    path('teachers/courses/<int:pk>', views.CourseStatsView.as_view(), name="course"),
    path('teachers/topics/<int:pk>', views.TopicView.as_view(), name="topic"),
]
