from django.forms import ModelForm

from base.models import Group, Student


class SetTUIDForm(ModelForm):
    class Meta:
        model = Student
        fields = ['tucan_id']


class RegistrationForm(ModelForm):
    class Meta:
        model = Group
        fields = ['students']
