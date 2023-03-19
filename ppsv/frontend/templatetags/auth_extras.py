from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Checks if the user is in the given group or not

    :return: True, if the user is in the given group
    :rtype: Boolean
    """
    return user.groups.filter(name=group_name).exists()
