"""Purpose of this file
This file contains forms associated with the frontend.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.forms import ModelForm
from course.models import Student
from django.utils.translation import gettext_lazy as _


class NewUserForm(UserCreationForm):
	"""New User Form
	represents the form to create new users

	:attr email: Input Field for the email
	:type email: EmailField
	"""

	email = forms.EmailField(required=True)

	class Meta:
		"""Meta options
		This class handles all possible meta options that you can give to this form.
		:attr Meta.model: The model to which this form corresponds
		:type Meta.model: Model
		:attr Meta.fields: Including fields into the form
		:type Meta.fields: str or list[str]
		"""
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		"""Save function for saving the newly created user

		:param commit: if the user should be saved
		:return: user
		"""
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class NewStudentForm(ModelForm):
	"""New Student form
	represents the form for creating a new student for the current user.

	:attr tucan_id: The TUCaN-ID of the student
	:type tucan_id: CharField
	:attr firstname: The first name of the student
	:type firstname: CharField
	:attr lastname: The last name of the student
	:type lastname: CharField
	"""
	tucan_id = forms.CharField(min_length=8, max_length=8, required=True, label=_('student ID'))
	firstname = forms.CharField(max_length=200, required=True, label=_("first Name"))
	lastname = forms.CharField(max_length=200, required=True, label=_("last Name"))

	class Meta:
		"""Meta options
		This class handles all possible meta options that you can give to this form.
		:attr Meta.model: The model to which this form corresponds
		:type Meta.model: Model
		:attr Meta.fields: Including fields into the form
		:type Meta.fields: str or list[str]
		"""
		model = Student
		fields = ("tucan_id", "firstname", "lastname")


class UserLoginForm(AuthenticationForm):

	def __init__(self, *args, **kwargs):
		super(UserLoginForm, self).__init__(*args, **kwargs)

	username = UsernameField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': _('Username'), 'id': 'username'}), label='')
	password = forms.CharField(widget=forms.PasswordInput(
		attrs={
			'class': 'form-control',
			'placeholder': _('Password'),
			'id': 'password',
		}
	), label='')
