from django.views.generic import FormView

from base.forms import ConfirmationForm


class ConfirmationView(FormView):
    template_name = "confirmation.html"
    form_class = ConfirmationForm

    def get_preview(self):
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["preview"] = self.get_preview()
        return context
