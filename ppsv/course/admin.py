from django.contrib import admin

from .models import Course
from .models import Topic
from .models import Student
from .models import Group
from .models import TopicSelection
from .models import TextSaves


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'registration_deadline', 'cp', 'max_participants')
    list_filter = ['registration_deadline']
    search_fields = ['title']


admin.site.register(Course, CourseAdmin)


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'max_participants')
    search_fields = ['title', 'course']


admin.site.register(Topic, TopicAdmin)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('tucan_id', 'firstname', 'lastname')
    search_fields = ['tucan_id', 'firstname', 'lastname']


admin.site.register(Student, StudentAdmin)

""" For that to work Group needs group_nr as primary key
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_nr', 'size')
"""

admin.site.register(Group)
admin.site.register(TopicSelection)
admin.site.register(TextSaves)


admin.site.site_header = 'PPSV-Administration'
