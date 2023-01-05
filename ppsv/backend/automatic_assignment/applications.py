from course.models import TopicSelection, Topic
from backend.models import Assignment

all_applications = []
accepted_applications = []
for assignment in Assignment.objects.all():
    if assignment.topic in Topic.objects.all():
        for accepted_application in assignment.accepted_applications.all():
            accepted_applications.append((accepted_application.group, accepted_application.collection_number))
for application in TopicSelection.objects.all():
    if not (application.group, application.collection_number) in accepted_applications:
        all_applications.append(application)


class Applications:
    applications: []

    def __init__(self):
        self.applications = all_applications

    def add(self, application):
        self.applications.append(application)

    def accept(self, application):
        """If we accept we will also remove all applications from this group and collection"""
        for _application in self.applications:
            if _application.group == application.group and \
                    _application.collection_number == application.collection_number:
                self.applications.remove(_application)

    def get_applications_for_topic(self, topic):
        applications = []
        for application in self.applications:
            if application.topic == topic:
                applications.append(application)
        return applications

    def has_topic(self, topic):
        for application in self.applications:
            if application.topic == topic:
                return True
        return False

    def filter(self, predicate):
        applications = {}
        for application in self.applications:
            if predicate(application):
                if (application.group, application.collection_number) not in applications:
                    applications[(application.group, application.collection_number)] = []
                applications[(application.group, application.collection_number)].append(application)
        return applications
