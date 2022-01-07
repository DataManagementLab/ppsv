from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView
from course.models import TopicSelection


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def selection(request):
    template_name = 'frontend/selection.html'
    # faculties contains all distinct faculties
    faculties = models.Course.objects.order_by().values('faculty').distinct()
    topic_choices = []

    if request.method == "POST":
        print(request.POST)

        if 'faculty_button' in request.POST:
            # When a form is send by the POST method the chosen faculty will be set to the chosen faculty
            chosen_faculty = request.POST.get('faculty_button')
            chosen_course = "no_chosen_course"

            # Courses which are from the chosen faculty
            courses = models.Course.objects.filter(faculty=chosen_faculty)

            args = {'courses': courses, 'chosenCourse': chosen_course, "choiceSet": topic_choices, "faculties": faculties}
            """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                and faculties(contains all faculties)"""
            return render(request, template_name, args)

        elif 'course_button' in request.POST:

            chosen_course = int(request.POST.get('course_button'))

            if chosen_course == -1:
                hidden_course_id = request.POST.get('hidden_info')
                courses = models.Course.objects.get(id=hidden_course_id)
                courses = models.Course.objects.filter(faculty=courses.faculty)
                chosen_course = "no_chosen_course"
                args = {'courses': courses, 'chosenCourse': chosen_course, "choiceSet": topic_choices,
                        "faculties": faculties}
                """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                    and faculties(contains all faculties)"""
                return render(request, template_name, args)
            else:
                courses = models.Course.objects.get(id=chosen_course)
                courses = models.Course.objects.filter(faculty=courses.faculty)
                topic_choice_set = models.Topic.objects.filter(course=chosen_course)
                for choice_set in topic_choice_set:
                    topic_choices.append(choice_set)

                args = {"courses": courses, 'chosenCourse': chosen_course, "choiceSet": topic_choices,
                        "faculties": faculties}
                """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                    and faculties(contains all faculties)"""
                return render(request, template_name, args)

        elif 'topic_button' in request.POST:
            chosen_topic = int(request.POST.get('topic_button'))

            if chosen_topic == -1:
                hidden_info = int(request.POST.get('hidden_info'))
                courses = models.Course.objects.filter(topic=hidden_info)
                courses_in_same_faculty = models.Course.objects.filter(faculty=courses[0].faculty)
                topics = models.Topic.objects.filter(course=courses[0].id)
                for topic in topics:
                    topic_choices.append(topic)
                args = {'courses': courses_in_same_faculty, "choiceSet": topic_choices, "faculties": faculties,
                        "chosenTopic": chosen_topic, 'chosenCourse': courses[0].id}
                return render(request, template_name, args)
            else:
                courses = models.Course.objects.filter(topic=chosen_topic)
                courses_in_same_faculty = models.Course.objects.filter(faculty=courses[0].faculty)
                topics = models.Topic.objects.filter(course=courses[0].id)
                for topic in topics:
                    topic_choices.append(topic)

                # change abcd to logged in student
                student_group = models.Group.objects.get(students='abcd')
                selection_group = models.TopicSelection.objects.filter(group=student_group.id)
                already_selected = False

                for known_selection in selection_group:
                    if int(chosen_topic) == int(known_selection.topic.id):
                        already_selected = True

                #if not already_selected:
                    # create Group with students in inputtext
                    #selection = TopicSelection()
                    #selection.priority = 0
                    # change abcd to logged in student
                    #selection.group = models.Group.objects.get(students='abcd')
                    #selection.topic = models.Topic.objects.get(id=chosen_topic)
                    #selection.save()

                args = {'courses': courses_in_same_faculty, "choiceSet": topic_choices, "faculties": faculties, "chosenTopic": chosen_topic, 'chosenCourse': courses[0].id}
                """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                    and faculties(contains all faculties)"""
                return render(request, template_name, args)

    args = {"faculties": faculties}
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


def login(request):
    template_name = 'frontend/login.html'
    return render(request, template_name)
