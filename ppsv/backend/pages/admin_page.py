import traceback

from django.core.exceptions import ValidationError
from django.core.mail import get_connection, EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from base.models import Term, Group, TopicSelection
from ppsv import settings
from ..automatic_assignment import main as automatic_assigment
from ..models import Assignment, TermFinalization, AcceptedApplications


def handle_get_assignment_progress():
    """returns the status of the automatic assignment"""
    return JsonResponse({
        "running": automatic_assigment.running,
        "progress": automatic_assigment.progress,
        "eta": automatic_assigment.eta
    })


def handle_finalize(request):
    """locks all slot, if possible (no errors in any slot)
    """
    if request.POST.get("finalize") == 'true':
        for slot in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
            try:
                slot.clean()
            except ValidationError:
                return JsonResponse({
                    "success": "false",
                })
            else:
                if not slot.assigned_student_to_slot_count == 0 and \
                        slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                    return JsonResponse({
                        "success": "false",
                    })
        for assignment in Assignment.objects.all():
            if assignment.finalized_slot < 2:
                assignment.finalized_slot += 2
                assignment.save()
        fin = TermFinalization.objects.get_or_create(term=Term.get_active_term())[0]
        fin.finalized = True
        fin.save()
        return JsonResponse({
            "success": "true",
        })
    else:
        fin = TermFinalization.objects.get_or_create(term=Term.get_active_term())[0]
        if fin.mails_send:
            return HttpResponse(status=500,
                                content="Emails got already send for this Term. Term is not changeable anymore")
        for assignment in Assignment.objects.all():
            if assignment.finalized_slot > 1:
                assignment.finalized_slot -= 2
                assignment.save()
        fin.finalized = False
        fin.save()
        return JsonResponse({
            "success": "true",
        })


def handle_start_automatic_assignment(request):
    """starts an automatic assignment if it is not running"""
    override = request.POST.get('override') == 'true'
    if not automatic_assigment.running:
        automatic_assigment.start_algo(override)
    return HttpResponse(status=205)


def handle_change_term(request):
    """changes the active term"""
    old_active_term = Term.get_active_term()
    if old_active_term != None:
        old_active_term.active_term = False
        old_active_term.save()
    new_active_term = Term.objects.get(name=request.POST.get("newTerm"))
    new_active_term.active_term = True
    new_active_term.save()
    return HttpResponse(status=205)


def handle_remove_broken_slots():
    """removes all broken slots from the database"""
    for slot in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        try:
            slot.clean()
        except ValidationError:
            slot.delete()
        else:
            if not slot.assigned_student_to_slot_count == 0 and \
                    slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                slot.delete()
    return HttpResponse(status=205)


def handle_send_mail():
    """
    sends an email to all students that have selected a topic in the current term.
    If emails have already been sent or the current term is not finalized, this function will return an error.
    """

    term = Term.get_active_term()
    if not TermFinalization.is_finalized(term):
        return HttpResponse(status=500, content="Term needs to be finalized")
    term_info = TermFinalization.objects.get(term=term)
    if term_info.mails_send:
        return HttpResponse(status=500, content="Emails got already send for this Term")

    mails = {}
    for group in Group.objects.filter(term=Term.get_active_term()):
        for student in group.students.all():
            if student not in mails:
                mails[student] = None
            else:
                break
            query = AcceptedApplications.objects.filter(topic_selection__group__students__in=[student],
                                                        topic_selection__group__term=Term.get_active_term())
            email_body_german = ""
            email_body_english = ""
            if query.exists():
                email_body_german += '<h3>Ihnen (oder Ihren Gruppen) wurden folgenden Themen zugewiesen</h3><ul>'
                email_body_english += '<h3>You (or your Groups) were assigned to the following Topics</h3><ul>'
                for accepted_application in query.all():
                    email_body_german += '<li>' + str(accepted_application.topic_selection.topic.course) + " "
                    email_body_german += str(accepted_application.topic_selection.topic)
                    email_body_english += '<li>' + str(accepted_application.topic_selection.topic.course) + " "
                    email_body_english += str(accepted_application.topic_selection.topic)
                    if accepted_application.topic_selection.group.size > 1:
                        email_body_german += "; " + str(accepted_application.topic_selection.group.get_display)
                        email_body_english += "; " + str(accepted_application.topic_selection.group.get_display)
                    email_body_german += '</li>'
                    email_body_english += '</li>'
                email_body_german += '</ul>'
                email_body_german += '<h3> Bitte melden Sie sich zeitnah in TUCAN zu diesen Kursen an.</h3>'
                email_body_english += '</ul>'
                email_body_english += '<h3> Please register as fast as possible for these Topics in TUCAN.</h3>'
            elif TopicSelection.objects.filter(group__students__in=[student], collection_number__gt=0,
                                               group__term=Term.get_active_term()).exists():
                email_body_german += '<h3>Ihnen (oder Ihren Gruppen) wurde leider keiner der gewünschten Plätze zugewiesen.</h3>'
                email_body_english += '<h3>Unfortunately, you (or your Groups) did not get any of your chosen Topics.</h3>'
            mails[student] = "* english version below *" + email_body_german + "\n" + \
                             "------------------------------------------------------------------------------------------------------" + \
                             "\n" + email_body_english

    connection = get_connection(
        username=None,
        password=None,
        fail_silently=True,
    )

    subject = 'Information zur Praktikums- und Seminarplatzvergabe ' + term.name + ' / Information for Internship & Seminar Allocation ' + term.name
    from_email = "PPSV <info@ppsv.tu-darmstadt.de>"

    messages = [
        EmailMultiAlternatives(
            subject=subject,
            body="<html><head></head><body>" + html_message + "</body></html>",
            from_email=from_email,
            to=[student.email],
            connection=connection,
        )
        for student, html_message in mails.items()
    ]
    for m in messages:
        m.content_subtype = 'html'
    term_info.mails_send = True
    term_info.save()

    if connection.send_messages(messages):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request
    """
    try:
        if "action" not in request.POST:
            return HttpResponse(status=501,
                                content="POST request didn't specify an action. Please report this and the actions you"
                                        " took to get this message to the administrator!")

        action = request.POST.get("action")

        if action == "getAssignmentProgress":
            return handle_get_assignment_progress()
        if action == "finalize":
            return handle_finalize(request)
        if action == "startAutomaticAssignment":
            return handle_start_automatic_assignment(request)
        if action == "changeTerm":
            return handle_change_term(request)
        if action == "removeBrokenSlots":
            return handle_remove_broken_slots()
        if action == "sendEmails":
            return handle_send_mail()

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took to "
                                    f"get this message to an administrator!")
    except Exception as e:
        if settings.DEBUG:
            print(traceback.format_exc())
        return HttpResponse(status=500, content=f"request caused an exception: \n {e}")


def render_site(request):
    """
    handles the rendering of the page.

    :param request: the handled request
    :param args: Arguments for rendering. When none given, an empty array is created

    :return: The rendered site
    :rtype: render() object
    """
    args = {}
    template_name = 'backend/control_flow.html'

    args["running"] = automatic_assigment.running
    args["terms"] = list(Term.objects.all())
    args["activeTerm"] = Term.get_active_term()

    return render(request, template_name, args)


def control_flow(request):
    """The view for the custom django admin page.

    :param request: the given request send by the assignment html-page
    In case of the request type being a 'POST' it will be handled by the handle_post method

    :return: a JsonResponse containing the information about the request if the request was a POST or a render()
    object otherwise
    """

    if not request.user.is_superuser:
        return redirect(reverse('admin:login') + '?next=' + reverse('assignments:manage'))

    # check if the request is a post
    if request.method == "POST":
        return handle_post(request)

    # if the request is not a post return a render of the default page
    return render_site(request)
