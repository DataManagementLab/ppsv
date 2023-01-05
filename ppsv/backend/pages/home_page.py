from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from backend import algorithm as algo
from backend import algo_new as algo_new
from backend.automatic_assignment import main as automatic_assignment


def handle_do_automatic_assignments(request):
    automatic_assignment.main(False)
    return JsonResponse(
        {
            'status': "done"
        })


def handle_post(request):
    if "action" not in request.POST:
        raise ValueError("POST request didn't specify an action")
    action = request.POST.get("action")

    if action == "doAutomaticAssignments":
        return handle_do_automatic_assignments(request)


def home_page(request):
    """The view for the home page.

    :param request: the given request send by the home html-page

    :return: a render() object
    :rtype: HttpResponse
    """
    if not request.user.is_staff:
        return redirect(reverse('admin:login') + '?next=' + reverse('backend:home_page'))

    if request.method == "POST":
        return handle_post(request)

    return render(request, 'backend/home.html')