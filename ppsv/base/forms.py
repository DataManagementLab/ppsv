from django.forms import forms, ModelForm, TextInput

from base.models import Course


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'type', 'organizer', 'description', 'registration_start', 'registration_deadline', 'cp', 'faculty', 'motivation_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_start'].widget.input_type = "date"
        self.fields['registration_deadline'].widget.input_type = "date"
