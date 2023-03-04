import traceback

from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from course.models import Term
from ppsv import settings
from ..automatic_assignment import main as automatic_assigment
from ..models import Assignment, TermFinalization


def handle_get_assignment_progress():
    return JsonResponse({
        "running": automatic_assigment.running,
        "progress": automatic_assigment.progress,
        "eta": automatic_assigment.eta
    })


def handle_finalize(request):
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
            "success": "yes",
        })
    else:
        for assignment in Assignment.objects.all():
            if assignment.finalized_slot > 1:
                assignment.finalized_slot -= 2
                assignment.save()
        fin = TermFinalization.objects.get_or_create(term=Term.get_active_term())[0]
        fin.finalized = False
        fin.save()
        return JsonResponse({
            "success": "no",
        })


def handle_start_automatic_assignment(request):
    override = request.POST.get('override') == 'true'
    if not automatic_assigment.running:
        automatic_assigment.start_algo(override)
    return HttpResponse(status=205)


def handle_change_term(request):
    old_active_term = Term.get_active_term()
    if old_active_term != None:
        old_active_term.active_term = False
        old_active_term.save()
    new_active_term = Term.objects.get(name=request.POST.get("newTerm"))
    new_active_term.active_term = True
    new_active_term.save()
    return HttpResponse(status=205)


def handle_remove_broken_slots():
    for slot in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        try:
            slot.clean()
        except ValidationError:
            slot.delete()
        else:
            if not slot.assigned_student_to_slot_count == 0 and \
                    slot.assigned_student_to_slot_count < slot.topic.min_slot_size:
                slot.accepted_applications.clear()
                slot.save()
    return HttpResponse(status=205)


def handle_post(request):
    """
    handles a POST request depending on the content of the action attribute.
    raises a ValueError if the action wasn't specified correctly.

    :param request: the handled request

    """
    try:
        if "action" not in request.POST:
            return HttpResponse(status=501,
                                content="POST request didn't specify an action. Please report this and the actions you took to get this message to the administrator!")

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

        return HttpResponse(status=501,
                            content=f"invalid request action: {action}. Please report this and the actions you took to get this message to an administrator!")
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
    template_name = 'backend/admin.html'

    args["running"] = automatic_assigment.running
    args["terms"] = list(Term.objects.all())
    args["activeTerm"] = Term.get_active_term()

    return render(request, template_name, args)


def admin_page(request):
    """The view for the custom django admin page.

    :param request: the given request send by the assignment html-page
    In case of the request type being a 'POST' it will be handled by the handle_post method

    :return: a JsonResponse containing the information about the request if the request was a POST or a render()
    object otherwise
    """

    if not request.user.is_superuser:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:assignment_page'))

    # check if the request is a post
    if request.method == "POST":
        return handle_post(request)

    # if the request is not a post return a render of the default page
    return render_site(request)
