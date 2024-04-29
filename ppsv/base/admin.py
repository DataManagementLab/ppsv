from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import Course, Term
from .models import CourseType
from .models import Group
from .models import Student
from .models import TextSaves
from .models import Topic
from .models import TopicSelection

admin.site.register(CourseType)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'active_term', 'registration_start', 'registration_deadline']
    list_display_links = ['name']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('get-term/<int:pk>/', self.get_term, name='get_term'),
        ]
        return my_urls + urls

    def get_term(self, request, pk):
        term = get_object_or_404(Term, pk=pk)
        data = {
            'reg_start': str(term.registration_start),
            'reg_end': str(term.registration_deadline),
        }
        return JsonResponse(data)


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
        (None,
         {'fields': ['title', 'type']}),
        ('Course Information', {
            'fields': ['description', 'motivation_text', 'cp', 'faculty', 'instructors', 'created_by', ]
        }),
        ('Date Information (Updates with Term)', {
            'fields': ['term', 'registration_start', 'registration_deadline', ],
        }),
    ]
    list_display = ('title', 'type', 'cp', 'faculty', 'term',)
    list_filter = ['term', 'faculty', ]
    search_fields = ['title', 'type__type']
    save_as = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('term')

    def term__reg_start(self, obj):
        return obj.term.registration_start

    def term__reg_end(self, obj):
        return obj.term.registration_deadline

    term__reg_start.short_description = 'Term registration start'
    term__reg_end.short_description = 'Term registration end'

    class Media:
        """Media
        references the path for scripts
        """
        js = ('https://code.jquery.com/jquery-3.6.0.min.js',
              '/static/admin/js/update_reg_on_term.js')


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
    list_display = ('title', 'course', 'max_slots', 'pk')
    search_fields = ['title', 'course__title']
    autocomplete_fields = ('course',)
    list_filter = ['course', 'course__term']


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
    list_display = ('get_display', 'size', 'term', 'pk')
    readonly_fields = ('get_display', 'size', 'term')
    list_filter = ['term']
    search_fields = ['students__tucan_id']
    fieldsets = [
        (None, {'fields': ['students', 'size', 'collection_count']}),
    ]
    filter_horizontal = ('students',)

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
    list_display = ('__str__', 'get_display', 'topic', 'collection_number', 'get_term', 'pk')
    readonly_fields = ('group', 'topic', 'motivation', 'priority', 'collection_number')
    search_fields = ('group__id', 'topic__course__title', 'topic__title', 'group__students__tucan_id')
    list_filter = ['topic__course__term', 'group']

    @admin.display(description=_('Term'))
    def get_term(self, obj):
        return obj.topic.course.term


admin.site.register(TopicSelection, TopicSelectionAdmin)
admin.site.register(TextSaves)

admin.site.site_header = 'PPSV-Administration'
