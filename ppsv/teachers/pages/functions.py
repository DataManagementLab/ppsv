from django.core.exceptions import MultipleObjectsReturned, ValidationError


def get_or_none(classmodel, **kwargs):
    """
    gets an object or throws an error if there are more than one in the database. If there are none in the database
    it will return None
    """
    try:
        return classmodel.objects.get(**kwargs)
    except MultipleObjectsReturned:
        raise ValidationError(f"Error in getting an object from {classmodel} with filters {kwargs}: "
                              f"Multiple objects found. \n Try to clear the slot, or contact an administrator.")
    except classmodel.DoesNotExist:
        return None


def get_or_error(classmodel, **kwargs):
    """
    gets an object or throws an error if there is none or more than one in the database
    """
    temp = get_or_none(classmodel, **kwargs)
    if temp is None:
        raise ValidationError(f"Error in getting an object from {classmodel} with filters {kwargs}: No objects found. "
                              f"\n Try to clear the slot, or contact an administrator.")
    return temp
