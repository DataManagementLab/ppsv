from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView, FormView, UpdateView, DeleteView, DetailView
from django.utils.translation import gettext_lazy as _

from base.models import Group, Student, TopicSelection, Topic
from base.views import ConfirmationView
from student.forms import GroupForm, SetTUIDForm, TopicSelectionForm


class RedirectToCompleteProfileViewMixin:
    def get(self, request, *args, **kwargs):
        if not hasattr(self.request.user, "student"):
            return redirect('student:complete-profile')
        return super().get(request, *args, **kwargs)


class Overview(RedirectToCompleteProfileViewMixin, ListView):
    model = Group
    template_name = "student/overview.html"
    context_object_name = "groups"

    def get_queryset(self):
        return self.request.user.student.group_set.filter(term__active_term=True)


class CompleteProfileView(LoginRequiredMixin, CreateView):
    model = Student
    template_name = "student/complete_profile.html"
    form_class = SetTUIDForm
    login_url = "/403"

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


class EditProfileView(RedirectToCompleteProfileViewMixin, LoginRequiredMixin, UpdateView):
    model = Student
    template_name = "student/edit_profile.html"
    form_class = SetTUIDForm
    success_url = reverse_lazy("student:overview")

    def get_object(self, queryset=None):
        return self.request.user.student

    def form_valid(self, form):
        r =  super().form_valid(form)
        messages.success(self.request, _("Profile updated"))
        return r


class RegisterView(RedirectToCompleteProfileViewMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "student/group_edit.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["students"] = self.request.user.student
        return initial

    def get_success_url(self):
        return reverse_lazy('student:register-select-topics', kwargs={"pk":self.object.pk})


class OwnGroupsOnlyMixin:
    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return self.request.user.student.group_set.get(pk=pk)


class EditGroupView(RedirectToCompleteProfileViewMixin, OwnGroupsOnlyMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "student/group_edit.html"

    success_url = reverse_lazy('student:overview')

    def form_valid(self, form):
        r = super().form_valid(form)
        messages.success(self.request, _("Group members updated"))
        return r

    def get_queryset(self):
        return super().get_queryset()


class EditRegistrationView(RedirectToCompleteProfileViewMixin, FormView):
    form_class = TopicSelectionForm
    template_name = "student/topic_selection.html"
    success_url = reverse_lazy("student:overview")
    model = Group

    def get_group(self):
        pk = self.kwargs.get("pk")
        group = get_object_or_404(Group, pk=pk)

        if self.request.user.student not in group.students.all():
            raise PermissionDenied()
        return group

    def form_valid(self, form):
        group = self.get_group()

        # Delete old registrations
        group.topicselection_set.all().delete()

        # Store Topic Selections
        topics_by_pk = {t.pk: t for t in form.cleaned_data['multivalto']}
        for i, pk in enumerate(self.request.POST.getlist('multivalto')):
            TopicSelection.objects.create(
                group=group,
                topic=topics_by_pk[int(pk)],
                priority=i+1
            )

        messages.success(self.request, _("Registration saved"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_group()
        context['selected_topics'] = [ts.topic for ts in group.topicselection_set.all()]
        context['unselected_topics'] = [topic for topic in Topic.currently_selectable() if topic not in context['selected_topics']]
        return context


class WithdrawRegistrationView(RedirectToCompleteProfileViewMixin, OwnGroupsOnlyMixin, ConfirmationView, DeleteView):
    title = _("Withdraw registration?")
    success_url = reverse_lazy("student:overview")
    model = Group

    def get_success_url(self):
        messages.info(self.request, _("Registration withdrawn"))
        return super().get_success_url()


class LoginRequiredView(TemplateView):
    template_name = "student/login_required.html"
