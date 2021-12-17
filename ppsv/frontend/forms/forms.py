from django import forms


class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(label='E-Mail')


class FacultyForm(forms.Form):
    faculty = forms.CharField(required=False)
