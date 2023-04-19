from django.forms import forms, ModelForm, TextInput

from base.models import Course


class ConfirmationForm(forms.Form):
    pass


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'type', 'organizer', 'description', 'registration_start', 'registration_deadline', 'cp', 'faculty', 'motivation_text']

    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial = {**self.initial, **kwargs['initial']}
        self.fields['registration_start'].widget.input_type = "date"
        self.fields['registration_deadline'].widget.input_type = "date"
