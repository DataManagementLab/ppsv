from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView
from django.utils.translation import gettext_lazy as _

from base.models import Group, Student
from student.forms import RegistrationForm, SetTUIDForm


class RedirectToCompleteProfileViewMixin:
    def get(self, request, *args, **kwargs):
        if not hasattr(self.request.user, "student"):
            return redirect('student:complete-profile')
        return super().get(request, *args, **kwargs)


class Overview(RedirectToCompleteProfileViewMixin, ListView):
    model = Group
    template_name = "student/overview.html"

    def get_queryset(self):
        return self.request.user.student.group_set.all()


class CompleteProfileView(CreateView):
    model = Student
    template_name = "student/complete_profile.html"
    form_class = SetTUIDForm

    def get(self, request, *args, **kwargs):
        if hasattr(self.request.user, "student"):
            return redirect('student:overview')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, _("Profile information saved"))
        return redirect("student:overview")


class RegisterView(RedirectToCompleteProfileViewMixin, CreateView):
    model = Group
    form_class = RegistrationForm
    template_name = "student/register.html"
