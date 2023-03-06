import copy

from backend.automatic_assignment.dataclasses import TempAssignment, TempApplication, TempTopic
from backend.automatic_assignment.my_dict_list import MyDictList
from backend.models import Assignment, AcceptedApplications
from backend.pages.functions import get_score_for_not_assigned
from course.models import Topic, Term, TopicSelection

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
        for slot in self.assignments[application.topic_id]:
            if slot.slot_id == slot_id:
                slot.accepted_applications.append(application)
                return
        self.assignments[application.topic_id].append(TempAssignment(topic_id=application.topic_id,
                                                                     slot_id=slot_id,
                                                                     accepted_applications=[application],
                                                                     locked=False))

    def get_remaining_space_in_slot(self, topic_id, slot_id):
        for assignment in self.get_assignments(topic_id):
            if assignment.slot_id == slot_id:
                if assignment.locked > 0:
                    return 0
                return topic_data[topic_id].max_slot_size - assignment.size
        return topic_data[topic_id].max_slot_size

    def score(self, applications):
        """returns the score for the all saved assignments. will use all open applications to find collections of groups
         that are not fulfilled. These will result in negativ scoring values. The range is depending on the number of
          collections. Can return a negative value. Higher values should represent a better score"""
        score = 0
        for slot in self.assignments.values():
            for assignment in slot:
                score += assignment.score
        # minus score für nicht zugewiesene gruppen
        score += get_score_for_not_assigned() * len(applications.applications_for_group.keys())
        return score

    def save_to_database(self, term):
        for assignment in Assignment.objects.filter(topic__course__term=term):
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
