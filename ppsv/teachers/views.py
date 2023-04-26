from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.views.generic import CreateView, ListView, DetailView

from backend.models import Assignment
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
        context["topics"] = self.object.topic_set.order_by('title') \
            .annotate(selected_count=Count("topicselection__group__students")) \
            .annotate(favorite_count=Count("topicselection__group__students", filter=Q(topicselection__priority=1)))
        context["applications"] = TopicSelection.objects.filter(topic__course=self.object)
        context["assignments"] = []

        context['students_assigned'] = 0
        for a in Assignment.objects.select_related('topic').order_by('topic__title').filter(topic__course=self.object):
            students = []
            for ts in a.accepted_applications.select_related('group').prefetch_related('group__students').all():
                for s in ts.group.students.all():
                    students.append(s.tucan_id)
            context["assignments"].append({
                "topic": a.topic,
                "count": len(students),
                "students": ", ".join(students),
            })
            context['students_assigned'] += len(students)
        return context


class AddCourseView(TeacherMixin, CreateView):
    model = Course
    template_name = "teachers/course_add.html"
    form_class = CourseForm
