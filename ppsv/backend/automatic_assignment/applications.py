import copy

from backend.automatic_assignment.my_dict_list import MyDictList
from backend.models import Assignment, AcceptedApplications
from course.models import TopicSelection, Topic, Term

init_applications_for_topic = MyDictList()
init_applications_for_group = MyDictList()


def init_applications(override_assignments):
    """inits the applications as is the stand of the database right now. this should be used for the whole automatic
    assignment process and not be changed. If override_assignments is True all non-locked assignments could be
    overwritten by the algorithm. init_assignments and init_applications needs to get the same bool."""
    global init_applications_for_group
    global init_applications_for_topic
    init_applications_for_topic = MyDictList()
    init_applications_for_group = MyDictList()
    for topic in Topic.objects.filter(course__term=Term.get_active_term()):
        init_applications_for_topic[topic] = []
    init_accepted_applications = []
    for accepted_application in AcceptedApplications.objects.filter(
            assignment__topic__course__term=Term.get_active_term()):
        if (not override_assignments) or accepted_application.assignment.locked or accepted_application.locked:
            init_accepted_applications.append(accepted_application.topic_selection.dict_key)
    for application in TopicSelection.objects.filter(topic__course__term=Term.get_active_term()).order_by('priority'):
        if application.dict_key not in init_accepted_applications:
            init_applications_for_topic[application.topic].append(application)
            if application.dict_key not in init_applications_for_group:
                init_applications_for_group[application.dict_key] = []
            init_applications_for_group[application.dict_key].append(application)


class Applications:
    """Represents all applications for this iteration
    :attr applications_for_topic: applications in a dictionary by topic
    :type {}: the dictionary
    :attr applications_for_topic: applications in a dictionary by group and collection number as a tuple
    :type {}: the dictionary
    """
    applications_for_topic: MyDictList
    applications_for_group: MyDictList

    def __init__(self):
        self.applications_for_topic = copy.deepcopy(init_applications_for_topic)
        self.applications_for_group = copy.deepcopy(init_applications_for_group)

    def accept(self, application):
        """If we accept we will also remove all applications from this group and collection"""

        for application_for_group in self.applications_for_group[(application.group, application.collection_number)]:
            self.applications_for_topic[application_for_group.topic].remove(application_for_group)
        self.applications_for_group.remove((application.group, application.collection_number))

    def get_applications_for_topic(self, topic):
        """returns all applications for a given topic
        :return: all applications for a given topic
        :rtype: []
        """
        return self.applications_for_topic[topic]

    def get_applications_for_topic_with_max_size(self, topic, max_size):
        """returns all applications for a given topic with a maximum of max_size members
                :return: all applications for a given topic with a max_size
                :rtype: []
                """
        applications = []
        for application in self.get_applications_for_topic(topic):
            if application.group.size <= max_size:
                applications.append(application)
        return applications

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
