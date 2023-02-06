from django.core.exceptions import ValidationError
from django.db import models
from course.models import TopicSelection
from course.models import Topic
from course.models import Group


def possible_assignments_for_group(group_id, collection_number):
    """possible applications in collection
    :return: the number of possible applications of this group for the given collection
    :rtype: int
    """

    all_applications = all_applications_from_group(group_id, collection_number)
    possible_assignments_for_group = 0
    for application in all_applications:
        query_assignments_for_topic = Assignment.objects.filter(topic=application.topic)
        if query_assignments_for_topic.count() < application.topic.max_slot_size:
            possible_assignments_for_group += 1
            continue
        for slot in query_assignments_for_topic:
            if slot.open_places_in_slot_count >= application.group.size:
                possible_assignments_for_group += 1
                continue
    return possible_assignments_for_group


def possible_assignments_for_topic(topic):
    """
    Returns all assignments than ce be assigned to the given topic without exceeding its maximum slot size
    :param topic: the topic the search the possible assignments of
    """
    open_assignment_count = topic.max_slot_size * topic.max_slots
    for assignment in Assignment.objects.filter(topic=topic):
        open_assignment_count -= topic.max_slot_size - assignment.open_places_in_slot_count
    return open_assignment_count


def all_applications_from_group(group_id, collection_number):
    """
    Returns all applications in the collection of the given group.
    :param group_id: the id of the group
    :param collection_number: the number of the collection to return the applications of
    :return: a list containing all applications in the given collection of the given group sorted by their priority
    """
    return list(TopicSelection.objects.filter(group_id=group_id).filter(collection_number=collection_number).order_by('priority'))


def get_all_applications_by_collection():
    """returns a dictionary with a (group,collection_number) pair as key, containing all applications for this group in
     this collection
    """

    application_for_group = {}
    for application in TopicSelection.objects.all():
        if (application.group, application.collection_number) not in application_for_group:
            application_for_group[(application.group, application.collection_number)] = []
        application_for_group[(application.group, application.collection_number)].append(application)
    return application_for_group


def get_all_applications_in_assignments():
    """returns a list of (group,collection_number) pairs, containing all accepted applications"""
    all_accepted_applications = []
    for assignment in Assignment.objects.all():
        for accepted_application in assignment.accepted_applications.all():
            all_accepted_applications.append((accepted_application.group, accepted_application.collection_number))
    return all_accepted_applications


def get_score_for_assigned(priority):
    return 21 - min(11, priority)


def get_score_for_not_assigned():
    return -30


class Assignment(models.Model):
    """ Assignment

    This model represents a slot to which applications can be assigned. An Assignment contains a topic, a slotID, all
    assigned applications and can be finalized so that no applications can be assigned or removed from this assignment.

    :attr Assignment.topic: The foreign key of a topic
    :type Assignment.topic: ForeignKey
    :attr Assignment.slot_id: The foreign key of a topic selection
    :type Assignment.slot_id: PositiveIntegerField
    :attr Assignment.accepted_applications: The accepted applications
    :type Assignment.accepted_applications: ManyToManyField through class AcceptedApplications
    :attr Assignment.finalized_slot: 0 if the assignment is not finalized, 1 if the assignment is finalized on the
    assignment page, 2 if the assignment was finalized by an admin, but it previously wasn't finalized and 3 if the
    assignment was finalized by an admin and it previously was finalized on the assignment page
    :type Assignment.finalized_slot: PositiveIntegerField
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="Topic")
    slot_id = models.PositiveIntegerField("SlotID")
    accepted_applications = models.ManyToManyField(TopicSelection, verbose_name="Accepted Applications",
                                                   through="AcceptedApplications")
    finalized_slot = models.PositiveIntegerField(default=0)

    @property
    def open_places_in_topic_count(self):
        """places in topic
        :return: returns the count of all open places (per student) for the topic of this assignment
        :rtype: int
        """
        open_assignment_count = self.topic.max_slot_size * self.topic.max_slots
        for assignment in Assignment.objects.filter(topic=self.topic):
            open_assignment_count -= self.topic.max_slot_size - assignment.open_places_in_slot_count
        return open_assignment_count

    @property
    def locked(self):
        return False

    @property
    def open_places_in_slot_count(self):
        """places in slot
        :return: returns the count of all open assignments (per student) for this slot
        :rtype: int
        """
        open_assignment_count = self.topic.max_slot_size
        for applications in self.accepted_applications.all():
            open_assignment_count -= applications.group.size
        return open_assignment_count

    @property
    def assigned_student_to_topic_count(self):
        """assigned to topic
        :return: returns the count of all assigned students for the topic of this assignment
        :rtype: int
        """
        all_assignment_count = 0
        for assignment in Assignment.objects.filter(topic=self.topic):
            all_assignment_count += assignment.assigned_student_to_slot_count
        return all_assignment_count

    @property
    def assigned_student_to_slot_count(self):
        """assigned to slot
        :return: returns the count of all assigned students for this slot
        :rtype: int
        """
        assignment_count = 0
        for application in self.accepted_applications.all():
            assignment_count += application.group.size
        return assignment_count

    @property
    def max_assigned_student_to_slot(self):
        return self.topic.max_slot_size

    def __str__(self):
        if self.topic.is_group_topic:
            return "Slot " + str(self.slot_id) + " of topic \"" + self.topic.title + "\" [" + str(
                self.assigned_student_to_slot_count) + "/" + str(self.topic.max_slot_size) + "]"
        else:
            return "Slot " + str(self.slot_id) + " of topic \"" + self.topic.title + "\""

    def clean(self):
        # SlotID Unique
        query = Assignment.objects.filter(topic=self.topic, slot_id=self.slot_id)
        if query.exists() and not (query.count() == 1 and query.contains(self)):
            raise ValidationError("Slot IDs need to be unique")

        # # Groups cant be in multiple slots of the same topic
        # groups = []
        # for assignment in Assignment.objects.filter(topic=self.topic):
        #     groups.append(assignment.accepted_applications.groups.all())
        # for groups in groups:
        #     for group in groups.all():
        #         if self.groups.contains(group):
        #             raise ValidationError("This group is already in another slot")

        # check if max_slot_size of topic is not exceeded (if min_size is not satisfied the assignment can be stored but not published)
        student_count = self.assigned_student_to_slot_count

        if student_count > self.topic.max_slot_size:
            raise ValidationError("This assignment exceeds the maximum slot size of the assigned topic")


class AcceptedApplications(models.Model):
    """ AcceptedApplications

    This model represents that an application is accepted via the specified assignment. An AcceptedApplications contains
    an assignment, a TopicSelection and can be finalized so that it can't be changed anymore.

    :attr AcceptedApplications.assignment: The foreign key of an assignment
    :type AcceptedApplications.assignment: ForeignKey
    :attr AcceptedApplications.topic_selection: The foreign key of a topic selection
    :type AcceptedApplications.topic_selection: ForeignKey
    :attr AcceptedApplications.finalized_assignment: True if the assignment is finalized
    :type AcceptedApplications.finalized_assignment: BooleanField
    """
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    topic_selection = models.ForeignKey(TopicSelection, on_delete=models.CASCADE)
    finalized_assignment = models.BooleanField(default=False)
