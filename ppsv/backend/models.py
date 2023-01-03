from django.core.exceptions import ValidationError
from django.db import models
from course.models import TopicSelection
from course.models import Topic
from course.models import Group


def possible_assignments(group_id, collection_number):
    """possible applications in collection
    :return: the number of possible applications of this group for the given collection
    :rtype: int
    """

    all_applications = TopicSelection.objects.filter(group_id=group_id).filter(collection_number=collection_number)
    all_applications_count = all_applications.count()

    group_size = Group.objects.get(pk=group_id).size

    query_possible_assignments = Assignment.objects.filter(topic__in=all_applications.values_list("topic_id"))
    for assignment in query_possible_assignments:
        if not (assignment.open_places_in_slot_count >= group_size or
                query_possible_assignments.count() < assignment.topic.max_slots):
            all_applications_count -= 1

    return all_applications_count


class Assignment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="Topic")
    slot_id = models.PositiveIntegerField("SlotID")
    accepted_applications = models.ManyToManyField(TopicSelection, verbose_name="Accepted Applications")

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
            return "Slot " + str(self.slot_id) + " of " + self.topic.title + " [" + str(
                self.assigned_student_to_slot_count) + "/" + str(self.topic.max_slot_size) + "]"
        else:
            return "Slot " + str(self.slot_id) + " of " + self.topic.title

    def clean(self):
        # SlotID Unique
        query = Assignment.objects.filter(slot_id=self.slot_id)
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