from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import CreateView, ListView

from base.forms import CourseForm
from .pages.overview_page import overview_page
from base.models import Course


def overview(request):
    overview_page(request)


class TeacherMixin(PermissionRequiredMixin):
    permission_required = ('courses.can_edit')


class CoursesOverview(TeacherMixin, ListView):
    model = Course
    context_object_name = "courses"
    template_name = "teachers/courses.html"

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


class AddCourseView(TeacherMixin, CreateView):
    model = Course
    template_name = "teachers/course_add.html"
    form_class = CourseForm
