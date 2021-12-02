from django.contrib import admin

from .models import Course
from .models import Topic
from .models import Student
from .models import Group
from .models import TopicSelection
from .models import TextSaves

admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Student)
admin.site.register(Group)
admin.site.register(TopicSelection)
admin.site.register(TextSaves)
