from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models import Group, Student


class SetTUIDForm(ModelForm):
    class Meta:
        model = Student
        fields = ['tucan_id']


class RegistrationForm(ModelForm):
    class Meta:
        model = Group
        fields = ['students']

    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial = {**self.initial, **kwargs['initial']}
        self.fields["students"].widget.attrs = {'class': 'chosen-select'}
        self.fields["students"].label = _("Group members")
        self.fields["students"].help_text = _("Specify other group members here (if applicable)")
