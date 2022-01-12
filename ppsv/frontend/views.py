from django.http import HttpResponse
from django.shortcuts import render
from course import models
from django.views.generic import TemplateView
from course.models import TopicSelection, Group


def homepage(request):
    template_name = 'frontend/homepage.html'
    return render(request, template_name)


def selection(request):

    template_name = 'frontend/selection.html'
    all_faculties = models.Course.objects.order_by().values('faculty').distinct()

    # If a form with the method "post" is submitted by a button
    if request.method == "POST":

        # If a button with the name "faculty_button" is pressed in "selection.html"
        if 'faculty_button' in request.POST:

            # "chosen_faculty" contains the faculty id of the pressed "faculty_button"
            chosen_faculty = str(request.POST.get('faculty_button'))
            # "courses_in_chosen_faculty" is a QuerySet with all courses in the database
            # which are in the "chosen_faculty"
            courses_in_chosen_faculty = models.Course.objects.filter(faculty=chosen_faculty)

            args = {'courses': courses_in_chosen_faculty, "faculties": all_faculties}

            return render(request, template_name, args)

        # If a button with the name 'course_button' is pressed in "selection.html"
        elif 'course_button' in request.POST:

            # "chosen_course" contains the course id of the pressed "course_button"
            chosen_course = int(request.POST.get('course_button'))

            # If the value of "chosen_course" is -1, it means that the same button was already clicked
            # one request before. When the button is clicked the first time it opens an overview of
            # the topics which are in "chosen_course" So when the button is clicked a second time
            # it will close the overview. In order to close the overview, "chosen_course" must not be returned
            # with any value.
            if chosen_course == -1:
                # Because the value of "course_button" is now "-1" and not the actual course id,
                # we need to get the course id from an element named "hidden_course_id"
                course_id = int(request.POST.get('hidden_course_id'))

                # In order to still display all courses in the same faculty after we closed the overview for the
                # topics, we need to get all courses in the chosen faculty again
                courses_in_chosen_faculty = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=course_id).faculty)

                args = {'courses': courses_in_chosen_faculty, "faculties": all_faculties}

                return render(request, template_name, args)

            # If the "course_button" is clicked the first time, we need to get all topics in thr chosen course
            else:
                # In order to still display all courses in the same faculty after we closed the overview for the
                # topics, we need to get all courses in the chosen faculty again
                courses_in_chosen_faculty = models.Course.objects.filter(
                    faculty=models.Course.objects.get(id=chosen_course).faculty)
                # "topic_choice_set" contains all topics in the chosen course
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course)

                args = {"courses": courses_in_chosen_faculty, 'chosen_course': chosen_course,
                        "topics_in_chosen_course": topics_in_chosen_course, "faculties": all_faculties}

                return render(request, template_name, args)

        # If a button with the name 'topic_button' is pressed in "selection.html"
        elif 'topic_button' in request.POST:

            # "chosen_topic" contains the topic id of the pressed "topic_button"
            chosen_topic = int(request.POST.get('topic_button'))

            # If the value of "chosen_topic" is -1, it means that the same button was already clicked
            # one request before. When the button is clicked the first time it opens a form to select the
            # chosen topic. So when the button is clicked a second time it will close the form.
            # In order to close the form, "chosen_topic" must not be returned with any value.
            if chosen_topic == -1:

                # Because the value of "topic_button" is now "-1" and not the actual topic id,
                # we need to get the topic id from an element named "hidden_topic_id"
                topic_id = int(request.POST.get('hidden_topic_id'))

                # "chosen_course" contains the course which contains the chosen topic
                chosen_course = models.Course.objects.get(topic=topic_id)

                # "course_of_chosen_topic" contains all courses which have the same faculty as the "chosen_course"
                courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

                # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

                args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                        "faculties": all_faculties, 'chosen_course': chosen_course.id}

                return render(request, template_name, args)

            # If the "topic_button" is clicked the first time
            else:

                # "chosen_course" contains the course which contains the chosen topic
                chosen_course = models.Course.objects.get(topic=chosen_topic)

                # "course_of_chosen_topic" contains all courses which have the same faculty as the "chosen_course"
                courses_in_same_faculty = models.Course.objects.filter(faculty=chosen_course.faculty)

                # "topics_in_chosen_course" contains all topics which are in the same course as the chosen topic
                topics_in_chosen_course = models.Topic.objects.filter(course=chosen_course.id)

                args = {'courses': courses_in_same_faculty, "topics_in_chosen_course": topics_in_chosen_course,
                        "faculties": all_faculties, "chosen_topic": chosen_topic,
                        'chosen_course': chosen_course.id}

                return render(request, template_name, args)

        elif 'select_topic_button' in request.POST:

            # Hier sind keine Kommentare weil der Code sich nach dem Merg ändern wird

            # change abcd to logged in student
            student_group = models.Group.objects.get(students='abcd')

            if not student_group:
                print("Empty")
                """
                # Creating a group for the student
                created_group = Group()
                # Change abds to user Tu-ID
                created_group.students.set(models.Student.objects.get(tucan_id='abcd'))
                created_group.save()
                """

            # change abcd to logged in student
            student_group = models.Group.objects.get(students='abcd')
            selections_with_group = models.TopicSelection.objects.filter(group=student_group.id)
            chosen_topic = int(request.POST.get('select_topic_button'))
            success = ''

            already_selected = False
            for known_selection in selections_with_group:
                if int(chosen_topic) == int(known_selection.topic.id):
                        already_selected = True
                        success = 'already_selected'

            if not already_selected:
                # create Group with students in inputtext
                user_selection = TopicSelection()
                user_selection.priority = 0
                # change abcd to logged in student
                user_selection.group = models.Group.objects.get(students='abcd')
                user_selection.topic = models.Topic.objects.get(id=chosen_topic)
                user_selection.save()
                success = 'success'

            courses_in_chosen_faculty = models.Course.objects.filter(topic=chosen_topic)
            courses_in_same_faculty = models.Course.objects.filter(faculty=courses_in_chosen_faculty[0].faculty)
            topics_in_chosen_course = models.Topic.objects.filter(course=courses_in_chosen_faculty[0].id)

            chosen_topic = -1

            args = {'courses': courses_in_same_faculty, "topic_in_chosen_course": topics_in_chosen_course, "faculties": all_faculties,
                    "chosen_topic": chosen_topic, 'chosen_course': courses_in_chosen_faculty[0].id, 'success': success}
            """ Returns args which contains courses(filtered by a chosen faculty), topic_choices(all topics in courses) 
                and faculties(contains all faculties)"""
            return render(request, template_name, args)

    args = {"faculties": all_faculties}
    return render(request, template_name, args)


def overview(request):
    template_name = 'frontend/overview.html'
    return render(request, template_name)


def groups(request):
    template_name = 'frontend/groups.html'
    return render(request, template_name)


def login(request):
    template_name = 'frontend/login.html'
    return render(request, template_name)
