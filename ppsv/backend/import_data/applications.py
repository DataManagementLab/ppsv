import copy

from backend.automatic_assignment.dataclasses import TempApplication
from backend.automatic_assignment.my_dict_list import MyDictList
from backend.models import AcceptedApplications
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
        init_applications_for_topic[topic.pk] = []
    init_accepted_applications = []
    for accepted_application in AcceptedApplications.objects.filter(
            assignment__topic__course__term=Term.get_active_term()):
        if (not override_assignments) or accepted_application.assignment.locked or accepted_application.locked:
            init_accepted_applications.append(accepted_application.topic_selection.dict_key)
    for application in TopicSelection.objects.filter(topic__course__term=Term.get_active_term(),
                                                     collection_number__gt=0).order_by('priority'):
        if application.dict_key not in init_accepted_applications:
            temp_application = TempApplication(
                id=application.pk,
                size=application.group.size,
                priority=application.priority,
                topic_id=application.topic.pk,
                collection_id=application.collection_number,
                locked=False,
                group_id=application.group.pk
            )
            init_applications_for_topic[application.topic.pk].append(temp_application)
            if (application.group_id, application.collection_number) not in init_applications_for_group:
                init_applications_for_group[(application.group_id, application.collection_number)] = []
            init_applications_for_group[(application.group_id, application.collection_number)].append(temp_application)


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
        """If we accept we will also remove all applications from this group and collection
        """
        for application_for_group in self.applications_for_group[application.dict_key]:
            self.applications_for_topic[application_for_group.topic_id].remove(application_for_group)
        self.applications_for_group.remove(application.dict_key)

    def get_applications_for_topic(self, topic_id):
        """returns all applications for a given topic
        :return: all applications for a given topic
        :rtype: []
        """
        return self.applications_for_topic[topic_id]

    def get_application(self, application_id):
        """returns the TempApplication to the give application_id
                :return: the TempApplication to the give application_id
                :rtype: TempApplication
                """
        for topic in self.applications_for_group.keys():
            for app in self.applications_for_group[topic]:
                if app.id == application_id:
                    return app

    def application_locked(self, application_id):
        """
        returns true if any application in the collection of the given id is locked, otherwise false
        """
        if self.get_application(application_id) is None:
            return True
        return False
