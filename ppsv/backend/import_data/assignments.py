import copy

from backend.automatic_assignment.dataclasses import TempAssignment, TempApplication, TempTopic
from backend.automatic_assignment.my_dict_list import MyDictList
from backend.models import Assignment, AcceptedApplications
from base.models import Topic, Term, TopicSelection

all_assignments = MyDictList()
topic_data = MyDictList()


def init_assignments(override_assignments):
    """inits the assignments as is the stand of the database right now. this should be used for the whole automatic
    assignment process and not be changed. If override_assignments is True all non-locked assignments could be
    overwritten by the algorithm."""
    global all_assignments
    all_assignments = MyDictList()
    for topic in Topic.objects.filter(course__term=Term.get_active_term()):
        all_assignments[topic.pk] = []
        topic_data[topic.pk] = TempTopic(
            min_slot_size=topic.min_slot_size,
            max_slot_size=topic.max_slot_size,
            slots=topic.max_slots,
            topic=topic
        )
    for assignment in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        handled_locked_applications = []
        if assignment.locked or not override_assignments:
            if assignment.locked:
                applications = []
                for application in AcceptedApplications.objects.filter(assignment=assignment):
                    handled_locked_applications.append(application.pk)
                    applications.append(TempApplication(
                        id=application.topic_selection.pk,
                        priority=application.topic_selection.priority,
                        topic_id=assignment.topic.pk,
                        size=application.topic_selection.group.size,
                        locked=application.finalized_assignment,
                        collection_id=application.topic_selection.collection_number,
                        group_id=application.topic_selection.group.pk
                    ))
                all_assignments[assignment.topic.pk].append(TempAssignment(
                    topic_id=assignment.topic.pk,
                    slot_id=assignment.slot_id,
                    accepted_applications=applications,
                    locked=assignment.finalized_slot))
        else:
            for application in AcceptedApplications.objects.filter(assignment=assignment):
                if application.locked and application.pk not in handled_locked_applications:
                    handled_locked_applications.append(application.pk)
                    temp_application = TempApplication(
                        id=application.topic_selection.pk,
                        priority=application.topic_selection.priority,
                        topic_id=assignment.topic.pk,
                        size=application.topic_selection.group.size,
                        locked=application.finalized_assignment,
                        collection_id=application.topic_selection.collection_number,
                        group_id=application.topic_selection.group.pk
                    )
                    all_assignments[assignment.topic.pk].append(TempAssignment(topic_id=assignment.topic.pk,
                                                                               slot_id=assignment.slot_id,
                                                                               accepted_applications=[temp_application],
                                                                               locked=0))


class Assignments:
    """Represents all assignments for this iteration
    """
    assignments: MyDictList()

    def __init__(self):
        self.assignments = copy.deepcopy(all_assignments)

    def get_assignments(self, topic_id):
        """Returns all assignments for the given topic"""
        return self.assignments[topic_id]

    def add_application(self, application, slot_id):
        """adds one application to a slot"""

        # slot id to high
        if slot_id > topic_data[application.topic_id].slots:
            return False, 'Slot-ID exceed number of slots in Topic.'

        # collection already satisfied
        if self.check_collection_satisfied(application):
            return False, 'Collection of the application is already satisfied.'

        slot_found = False
        for slot in self.assignments[application.topic_id]:
            if slot.slot_id == slot_id:
                slot_found = True
                if application.size > self.get_remaining_space_in_slot(application.topic_id, slot_id):
                    return False, 'Application ' + str(application.id) + ' does not fit in slot.'
                slot.accepted_applications.append(application)

        if not slot_found:
            self.assignments[application.topic_id].append(TempAssignment(topic_id=application.topic_id,
                                                                         slot_id=slot_id,
                                                                         accepted_applications=[application],
                                                                         locked=False))

        return True, 'All worked fine.'

    def get_remaining_space_in_slot(self, topic_id, slot_id):
        """returns the remaining places in the specified"""
        for assignment in self.get_assignments(topic_id):
            if assignment.slot_id == slot_id:
                if assignment.locked > 0:
                    return 0
                return topic_data[topic_id].max_slot_size - assignment.size
        return topic_data[topic_id].max_slot_size

    def save_to_database(self, term, faculties):
        """saves the new assignments to the database only changing the faculties of the imported data"""
        for assignment in Assignment.objects.filter(topic__course__term=term, topic__course__faculty__in=faculties):
            assignment.delete()
        for assignments in self.assignments.values():
            for assignment in assignments:
                new_assignment = Assignment.objects.create(
                    topic=topic_data[assignment.topic_id].topic,
                    slot_id=assignment.slot_id,
                    finalized_slot=assignment.locked
                )
                for application in assignment.accepted_applications:
                    AcceptedApplications.objects.create(
                        assignment=new_assignment,
                        topic_selection=TopicSelection.objects.get(pk=application.id),
                        finalized_assignment=application.locked
                    )

    def check_collection_satisfied(self, application):
        """returns if the collection the group from this application is satisfied or not"""
        for topic_id in self.assignments.keys():
            for assignment in self.assignments[topic_id]:
                for app in assignment.accepted_applications:
                    if app.group_id == application.group_id and app.collection_id == application.collection_id:
                        return True
        return False
