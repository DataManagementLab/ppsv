from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.views.generic import CreateView, ListView, DetailView

from base.forms import CourseForm
from base.models import Course, TopicSelection
from .pages.overview_page import overview_page


def overview(request):
    overview_page(request)


class TeacherMixin(PermissionRequiredMixin):
    permission_required = ('base.courses.can_edit')


class CoursesOverview(TeacherMixin, ListView):
    model = Course
    context_object_name = "courses"
    template_name = "teachers/courses.html"

    def get_queryset(self):
        return self.request.user.courses.all()


class CourseStatsView(TeacherMixin, DetailView):
    model = Course
    context_object_name = "course"
    template_name = "teachers/course.html"

    def get_queryset(self):
        return super().get_queryset().select_related('term', 'type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = self.object.topic_set \
            .annotate(selected_count=Count("topicselection__group__students")) \
            .annotate(favorite_count=Count("topicselection__group__students", filter=Q(topicselection__priority=1)))
        context["applications"] = TopicSelection.objects.filter(topic__course=self.object)
        context["assignments"] = self.object.topic_set.\
            annotate(assigned_count=Count("assignment__accepted_applications__group__students"))
        return context


class AddCourseView(TeacherMixin, CreateView):
    model = Course
    template_name = "teachers/course_add.html"
    form_class = CourseForm
