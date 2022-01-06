from django.http import HttpResponse
from django.shortcuts import render, redirect
from course import models
from .forms.forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def selection(request):
    template_name = 'frontend/selection.html'
    # All courses in the database are saved in courses
    courses = models.Course.objects.all()
    # All topics in the database are saved in topics
    topics = models.Topic.objects.all()
    args = {'courses': courses, "topics": topics}
    # Returns args which contains all courses and topics in the database
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'

    # faculties contains all distinct faculties
    faculties = models.Course.objects.order_by().values('faculty').distinct()
    # topics contains all topics
    topics = models.Topic.objects.all()
    topic_choices = []

    chosen_faculty = ""

    if request.method == "POST":

        for i in range(len(faculties)):

            if faculties[i]['faculty'] in request.POST:
                # When a form is send by the POST method the chosen faculty will be set to the chosen faculty
                chosen_faculty = faculties[i]['faculty']
                print(chosen_faculty)

    # Courses which are from the chosen faculty
    courses = models.Course.objects.filter(faculty=chosen_faculty)

    # Topics which are in the chosen courses
    for selected_course in courses:
        topic_choices.append(models.Topic.objects.filter(course=selected_course))

    args = {'courses': courses, "topicChoices": topic_choices, "faculties": faculties}
    """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
        and faculties(contains all faculties)"""
    return render(request, template_name, args)


def groups(request):
    template_name = 'frontend/groups.html'
    return render(request, template_name)


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        print("login_request active")
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("frontend:homepage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})


def logout_request(request):
    print("logout_request active")
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("frontend:homepage")


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        print("register active")
        if form.is_valid():
            print("form is valid")
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("frontend:homepage")
        print("form is not valid")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})
