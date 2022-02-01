from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Course
from .models import Topic
from .models import Student
from .models import Group
from .models import TopicSelection
from .models import TextSaves


class CourseAdmin(admin.ModelAdmin):
    """Course admin

    Represents the Course model in the admin panel.

    :attr CourseAdmin.fieldsets: controls the layout of admin “add” and “change” pages
    :type CourseAdmin.fieldsets: list[tuple[None, dict[str, list[str]]] | tuple[__proxy__, dict[str, list[str]]] |...
    :attr CourseAdmin.list_display: Controls which fields are displayed on the change list page of the admin
    :type CourseAdmin.list_display: tuple[str, str, str, str, str]
    :attr CourseAdmin.list_filter: activates filters in the right sidebar of the change list page of the admin
    :type CourseAdmin.list_filter: list[str]
    :attr CourseAdmin.search_fields: enables a search box for titles on the admin change list page
    :type CourseAdmin.search_fields:  list[str]
    """
    fieldsets = [
        (None, {'fields': ['title', 'type']}),
        (_('Date Information'), {'fields': ['registration_start', 'registration_deadline']}),
        (_('Course Information'), {'fields': ['description', 'motivation_text', 'cp', 'faculty', 'organizer']}),
        (_('Participant Number'), {'fields': ['unlimited', 'max_participants']}),
        ]
    list_display = ('title', 'type', 'registration_deadline', 'cp', 'max_participants')
    list_filter = ['registration_deadline']
    search_fields = ['title']

    class Media:
        """Media
        references the path for scripts
        """
        js = ('/static/admin/js/hide_attribute.js',)


admin.site.register(Course, CourseAdmin)


class TopicAdmin(admin.ModelAdmin):
    """Topic admin

    Represents the Topic model in the admin panel.

    :attr TopicAdmin.list_display: controls which fields are displayed on the change list page of the admin
    :type TopicAdmin.list_display: tuple[str, str, str]
    :attr TopicAdmin.search_fields: enables a search box for titles and Courses on the admin change list page
    :type TopicAdmin.search_fields:  list[str, str]
    """
    list_display = ('title', 'course', 'max_participants')
    search_fields = ['title', 'course']


admin.site.register(Topic, TopicAdmin)


class StudentAdmin(admin.ModelAdmin):
    """Student admin

    Represents the Student model in the admin panel.

    :attr StudentAdmin.list_display: controls which fields are displayed on the change list page of the admin
    :type StudentAdmin.list_display: tuple[str, str, str]
    :attr StudentAdmin.search_fields: enables a search box for titles and Courses on the admin change list page
    :type StudentAdmin.search_fields:  list[str, str, str]
    """
    list_display = ('tucan_id', 'firstname', 'lastname')
    search_fields = ['tucan_id', 'firstname', 'lastname']


admin.site.register(Student, StudentAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('get_display', 'size')
    readonly_fields = ('get_display', 'size',)
    fieldsets = [
        (None, {'fields': ['students', 'size', 'assignments']}),
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a ModelForm class for use in the admin add and change views.
        :return: ModelForm for adding and changing
        :rtype: ModelForm
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['students'].widget.can_add_related = False
        return form


admin.site.register(Group, GroupAdmin)
admin.site.register(TopicSelection)
admin.site.register(TextSaves)


admin.site.site_header = 'PPSV-Administration'
