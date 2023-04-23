import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from base.models import Group, Student, Topic


valid_tu_id = re.compile(r"^[a-zA-Z]{2}\d{2}[a-zA-Z]{4}$")


class SetTUIDForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['tucan_id']

    def clean_tucan_id(self):
        if not valid_tu_id.fullmatch(self.cleaned_data['tucan_id']):
            raise ValidationError(
                _("Your input does not follow the typical format of a TU ID. In case you are sure your input was correct "
                  "nevertheless, please contact the organizers."),
                code="invalid"
            )
        return self.cleaned_data['tucan_id']


class GroupForm(forms.ModelForm):
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


class TopicSelectionForm(forms.Form):
    multivalfrom = forms.ModelMultipleChoiceField(
        label=_("Available topics"),
        queryset=Topic.objects.all(),
        required=False,
    )
    multivalto = forms.ModelMultipleChoiceField(
        label=_("Selected topics"),
        queryset=Topic.objects.all(),
        required=False,
    )
