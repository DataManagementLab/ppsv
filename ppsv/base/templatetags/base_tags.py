from django import template
from django.apps import apps

register = template.Library()


@register.filter
def check_app_installed(name):
    return apps.is_installed(name)
