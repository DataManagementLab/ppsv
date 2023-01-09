import copy

from backend.models import Assignment
from course.models import TopicSelection, Topic

init_applications_for_topic = {}
init_applications_for_group = {}


def init_applications(override_assignments):
    """inits the applications as is the stand of the database right now. this should be used for the whole automatic
    assignment process and not be changed. If override_assignments is True all non-locked assignments could be
    overwritten by the algorithm. init_assignments and init_applications needs to get the same bool."""
    global init_applications_for_group
    global init_applications_for_topic
    init_applications_for_topic = {}
    init_applications_for_group = {}
    for topic in Topic.objects.all():
        init_applications_for_topic[topic] = []
    init_accepted_applications = []
    for assignment in Assignment.objects.all():
        if not override_assignments or assignment.locked:
            for accepted_application in assignment.accepted_applications.all():
                init_accepted_applications.append((accepted_application.group, accepted_application.collection_number))
    for application in TopicSelection.objects.all():
        if (application.group, application.collection_number) not in init_accepted_applications:
            init_applications_for_topic[application.topic].append(application)
            if (application.group, application.collection_number) not in init_applications_for_group:
                init_applications_for_group[(application.group, application.collection_number)] = []
            init_applications_for_group[(application.group, application.collection_number)].append(application)


class Applications:
    """Represents all applications for this iteration
    :attr applications_for_topic: applications in a dictionary by topic
    :type {}: the dictionary
    :attr applications_for_topic: applications in a dictionary by group and collection number as a tuple
    :type {}: the dictionary
    """
    applications_for_topic: {}
    applications_for_group: {}

    def __init__(self):
        self.applications_for_topic = copy.deepcopy(init_applications_for_topic)
        self.applications_for_group = copy.deepcopy(init_applications_for_group)

    def accept(self, application):
        """If we accept we will also remove all applications from this group and collection"""

        for application_for_group in self.applications_for_group.get(
                (application.group, application.collection_number)):
            self.applications_for_topic[application_for_group.topic].pop(
                self.applications_for_topic[application_for_group.topic].index(application_for_group))
        self.applications_for_group.pop((application.group, application.collection_number))

    def get_applications_for_topic(self, topic):
        """returns all applications for a given topic
        :return: all applications for a given topic
        :rtype: []
        """
        return self.applications_for_topic[topic]

    def get_applications_for_group(self, group, collection_number):
        """returns all applications for a given group and collection number
        :return: all applications for a given group and collection number
        :rtype: []
        """
        return self.applications_for_group[(group, collection_number)]

    def has_topic(self, topic):
        """returns true if there are applications for the given topic
        :return: true if there are applications for the given topic
        :rtype: bool
        """
        return topic in self.applications_for_topic


def print_group_for_topic(dict):
    """helper to print a applications_for_topic dict"""
    for key, value in dict.items():
        print(str(key[0]) + "," + str(key[1]) + ": " + str(value))


def print_topic_for_topic(dict):
    """helper to print a applications_for_group dict"""
    for key, value in dict.items():
        print(str(key) + ": " + str(value))
