from django.core.exceptions import ValidationError
from django.db import models
from course.models import TopicSelection
from course.models import Topic
from course.models import Group


def remaining_selections_count(group_id, collection_number):
    """open applications in collection
    :return: the number of open applications of this group for the given collection
    :rtype: int
    """
    all_applications = TopicSelection.objects.filter(group_id=group_id).filter(collection_number=collection_number)
    all_assignments = Assignment.objects.filter(groups__in=[all_applications[0].group],
                                                topic__in=[all_applications[0].topic])
    return all_applications.count() - all_assignments.count()


class Assignment(models.Model):
    """Assignment

    This model represents an assignment of a group to a slot of a topic. Multiple groups can be assigned to the same
    slot of a topic if their total student count does not exceed the max group size of the topic.

    :attr Assignment.topic: the topic the groups are assigned to
    :type Assignment.topic: ForeignKey - Topic
    :attr Assignment.groups: The groups that are assigned
    :type Assignment.groups: ManyToManyField - Group
    :attr Assignment.solt_id: The slot the groups are assigned to
    :type Assignment.slot_id: PositiveIntegerField
    :property Assignment.open_places_in_topic_count: the amount of available places in the assigned topic
    :type Assignment.open_places_in_topic_count: int
    :property Assignment.open_places_in_slot_count: the amount of available places in the assigned slot
    :type Assignment.open_places_in_slot_count: int
    :property Assignment.assigned_student_to_topic_count: the amount of students assigned to this topic
    :type Assignment.assigned_student_to_topic_count: int
    :property Assignment.assigned_student_to_slot_count:the amount of students assigned to this slot
    :type ment.assigned_student_to_slot_count: int
    """

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="Topic")
    groups = models.ManyToManyField(Group, verbose_name="Groups")
    slot_id = models.PositiveIntegerField("SlotID")

    @property
    def open_places_in_topic_count(self):
        """places in topic
        :return: returns the count of all open places (per student) for the topic of this assignment
        :rtype: int
        """
        open_assignment_count = self.topic.max_slot_size * self.topic.max_slots
        for assignment in Assignment.objects.filter(topic=self.topic):
            for group in assignment.groups.all():
                open_assignment_count -= group.size
        return open_assignment_count

    @property
    def open_places_in_slot_count(self):
        """places in slot
        :return: returns the count of all open assignments (per student) for this slot
        :rtype: int
        """
        open_assignment_count = self.topic.max_slot_size
        for group in self.groups.all():
            open_assignment_count -= group.size
        return open_assignment_count

    @property
    def assigned_student_to_topic_count(self):
        """assigned to topic
        :return: returns the count of all assigned students for the topic of this assignment
        :rtype: int
        """
        all_assignment_count = 0
        for assignment in Assignment.objects.filter(topic=self.topic):
            for group in assignment.groups.all():
                all_assignment_count += group.size
        return all_assignment_count

    @property
    def assigned_student_to_slot_count(self):
        """assigned to slot
        :return: returns the count of all assigned students for this slot
        :rtype: int
        """
        assignment_count = 0
        for group in self.groups.all():
            assignment_count += group.size
        return assignment_count

    @property
    def max_assigned_student_to_slot(self):
        return self.topic.max_slot_size

    # def __str__(self):
    #     return "Assignments for Topic " + self.topic.title + " [" + str(self.assigned_groups_all) + "/" + str((
    #             self.topic.max_slots * self.topic.max_GroupSize)) + "]: Slot " + str(self.slot_id)

    def __str__(self):
        if self.topic.is_group_topic:
            return "Slot " + str(self.slot_id) + " of " + self.topic.title + " [" + str(
                self.assigned_student_to_slot_count) + "/" + str(self.topic.max_slot_size) + "]"
        else:
            return "Slot " + str(self.slot_id) + " of " + self.topic.title

    def clean(self):
        # SlotID Unique
        query = Assignment.objects.filter(slot_id=self.slot_id)
        if query.exists() and not (query.count() == 1 and query.contains(self)):
            raise ValidationError("Slot IDs need to be unique")

        # Groups cant be in multiple slots of the same topic
        query = Assignment.objects.filter(topic=self.topic)
        groups = []
        for assignment in query:
            groups.append(assignment.groups.all())
        for groups in groups:
            for group in groups.all():
                if self.groups.contains(group):
                    raise ValidationError("This group is already in another slot")

        # check if max_slot_size of topic is not exceeded (if min_size is not satisfied the assignment can be stored but not published)
        student_count = self.assigned_student_to_slot_count

        if student_count > self.topic.max_slot_size:
            raise ValidationError("This assignment exceeds the maximum slot size of the assigned topic")
