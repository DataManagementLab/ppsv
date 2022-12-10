from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import Course
from .models import Topic
from .models import Student
from .models import Group
from .models import TopicSelection
from .models import TextSaves
from .models import CourseType


admin.site.register(CourseType)


class CourseAdmin(ImportExportMixin, admin.ModelAdmin):
    """Course admin

    Represents the Course model in the admin panel.

    :attr CourseAdmin.fieldsets: controls the layout of admin “add” and “change” pages
    :type CourseAdmin.fieldsets: list[tuple[None, dict[str, list[str]]] | tuple[__proxy__, dict[str, list[str]]] |...
    :attr CourseAdmin.list_display: Controls which fields are displayed on the change list page of the admin
    :type CourseAdmin.list_display: tuple[str, str, str, str, str]
    :attr CourseAdmin.list_filter: activates filters in the right sidebar of the change list page of the admin
    :type CourseAdmin.list_filter: list[str]
    :attr CourseAdmin.search_fields: enables a search box for titles on the admin change list page
    :type CourseAdmin.search_fields: list[str]
    """
    fieldsets = [
        (None, {'fields': ['title', 'type']}),
        ('Date Information', {'fields': ['registration_start', 'registration_deadline']}),
        ('Course Information', {'fields': ['description', 'motivation_text', 'cp', 'faculty', 'organizer']}),
    ]
    list_display = ('title', 'type', 'registration_deadline', 'cp')
    list_filter = ['registration_deadline']
    search_fields = ['title', 'type__type']

    class Media:
        """Media
        references the path for scripts
        """
        js = ('/static/admin/js/hide_attribute.js',)


admin.site.register(Course, CourseAdmin)


class TopicAdmin(ImportExportMixin, admin.ModelAdmin):
    """Topic admin

    Represents the Topic model in the admin panel.

    :attr TopicAdmin.list_display: controls which fields are displayed on the change list page of the admin
    :type TopicAdmin.list_display: tuple[str, str, str]
    :attr TopicAdmin.search_fields: enables a search box for titles and Courses on the admin change list page
    :type TopicAdmin.search_fields:  list[str, str]
    :attr TopicAdmin.autocomplete_fields: allows searching for courses while editing/creating topics
    :type TopicAdmin.autocomplete_fields: tuple[str, ]
    """
    list_display = ('title', 'course', 'max_slots')
    search_fields = ['title', 'course__title']
    autocomplete_fields = ('course', )

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a ModelForm class for use in the admin add and change views.
        :return: ModelForm for adding and changing
        :rtype: ModelForm
        """
        form = super().get_form(request, obj, **kwargs)
        # disable course creation during topic creation and editing
        form.base_fields['course'].widget.can_add_related = False
        return form

    class Media:
        js = (
            "/static/admin/js/TopicAdmin.js",
        )


admin.site.register(Topic, TopicAdmin)


class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
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


class GroupAdmin(ImportExportMixin, admin.ModelAdmin):
    """Group admin

    Represents the Group model in the admin panel.

    :attr GroupAdmin.list_display: controls which fields are displayed on the change list page of the admin
    :type GroupAdmin.list_display: tuple[str, str, str]
    :attr GroupAdmin.search_fields: enables a search box for titles and Courses on the admin change list page
    :type GroupAdmin.search_fields:  list[str, str, str]
    :attr GroupAdmin.fieldsets: controls the layout of admin “add” and “change” pages
    :type GroupAdmin.fieldsets: list[tuple[None, dict[str, list[str]]] | tuple[__proxy__, dict[str, list[str]]] |...
    :attr GroupAdmin.filter_horizontal: enables searching for students while creating or editing a group
    :type GroupAdmin.filter_horizontal: tuple[str, ]
    """
    list_display = ('get_display', 'size')
    readonly_fields = ('get_display', 'size',)
    fieldsets = [
        (None, {'fields': ['students', 'size', 'collection_count']}),
    ]
    filter_horizontal = ('students', )

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a ModelForm class for use in the admin add and change views.
        :return: ModelForm for adding and changing
        :rtype: ModelForm
        """
        form = super().get_form(request, obj, **kwargs)
        # disable student creation during group creation and editing
        form.base_fields['students'].widget.can_add_related = False
        return form


admin.site.register(Group, GroupAdmin)


class TopicSelectionAdmin(ImportExportMixin, admin.ModelAdmin):
    """Course admin

    Represents the TopicSelection model in the admin panel.

    :attr TopicSelectionAdmin.list_display: Controls which fields are displayed on the change list page of the admin
    :type TopicSelectionAdmin.list_display: tuple[str, str, str, str, str]
    :attr TopicSelectionAdmin.search_fields: enables a search box for titles on the admin change list page
    :type TopicSelectionAdmin.search_fields: list[str]
    :attr TopicSelectionAdmin.list_filter: activates filters in the right sidebar of the change list page of the admin
    :type TopicSelectionAdmin.list_filter: list[str]
    """
    list_display = ('__str__', 'get_display', 'topic', 'collection_number')
    readonly_fields = ('get_display', )
    search_fields = ('group__id', 'topic__title', 'collection_number')
    list_filter = ('topic', )

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a ModelForm class for use in the admin add and change views.
        :return: ModelForm for adding and changing
        :rtype: ModelForm
        """
        form = super().get_form(request, obj, **kwargs)
        # disable group and topic creation during group creation and editing
        form.base_fields['group'].widget.can_add_related = False
        form.base_fields['topic'].widget.can_add_related = False
        return form


admin.site.register(TopicSelection, TopicSelectionAdmin)
admin.site.register(TextSaves)


admin.site.site_header = 'PPSV-Administration'
