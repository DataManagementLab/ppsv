import copy
from dataclasses import dataclass

from backend.automatic_assignment.my_dict_list import MyDictList
from backend.models import Assignment, AcceptedApplications
from backend.pages.functions import get_score_for_assigned, get_score_for_not_assigned
from course.models import Topic, Term


@dataclass
class TempAssignment:
    """This class represents one temporary assignment for this iteration"""
    topic: Topic
    slot_id: int
    accepted_applications: []

    @property
    def score(self):
        """returns the score of this assignment in range [20,10], while 20 will be given for an application with
        priority 1, 19 for priority 2 and so on"""
        score = 0
        for application in self.accepted_applications:
            score += get_score_for_assigned(application.group.size, application.priority)
        return score

    @property
    def student_size(self):
        """returns how many students are in currently in this assignment(slot)"""
        size = 0
        for application in self.accepted_applications:
            size += application.group.size
        return size


all_assignments = MyDictList()
locked_assignments = {}
locked_applications = []


def init_assignments(override_assignments):
    """inits the assignments as is the stand of the database right now. this should be used for the whole automatic
    assignment process and not be changed. If override_assignments is True all non-locked assignments could be
    overwritten by the algorithm."""
    global all_assignments
    all_assignments = MyDictList()
    for topic in Topic.objects.filter(course__term=Term.get_active_term()):
        all_assignments[topic] = []
    for assignment in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        if assignment.locked or not override_assignments:
            if assignment.locked:
                locked_assignments[(assignment.topic, assignment.slot_id)] = assignment.finalized_slot
            all_assignments[assignment.topic].append(
                TempAssignment(topic=assignment.topic,
                               slot_id=assignment.slot_id,
                               accepted_applications=list(assignment.accepted_applications.all())))
        else:
            locked_apps = []
            for application in AcceptedApplications.objects.filter(assignment=assignment):
                if application.locked:
                    locked_apps.append(application.topic_selection)
                    locked_applications.append(application.topic_selection)
            if len(locked_apps) > 0:
                all_assignments[assignment.topic].append(TempAssignment(topic=assignment.topic,
                                                                        slot_id=assignment.slot_id,
                                                                        accepted_applications=locked_apps))


class Assignments:
    """Represents all assignments for this iteration
    """
    assignments: MyDictList()

    def __init__(self):
        self.assignments = copy.deepcopy(all_assignments)

    def get_assignments(self, topic):
        """Returns all assignments for the given topic"""
        return self.assignments[topic]

    def add_application(self, application, slot_id):
        """adds one application to a slot"""
        for slot in self.assignments[application.topic]:
            if slot.slot_id == slot_id:
                slot.accepted_applications.append(application)
                return
        self.assignments[application.topic].append(TempAssignment(topic=application.topic,
                                                                  slot_id=slot_id,
                                                                  accepted_applications=[application]))

    def get_remaining_space_in_slot(self, topic, slot_id):
        assignments = self.get_assignments(topic)
        for slot in assignments:
            if slot.slot_id == slot_id:
                return topic.max_slot_size - slot.accepted_applications
        return topic.max_slot_size

    def biggest_open_slot(self, topic):
        """returns a tuple of (slot_size, slot_id) for the biggest open slot of the given topic. will return (0,1) if
        there are no slots or no open slots for the given topic"""
        assignments = self.get_assignments(topic)
        if len(assignments) < topic.max_slots:
            return topic.max_slot_size, len(assignments) + 1
        open_slot_size = 0
        open_slot_id = 1
        for slot in assignments:
            if (topic.max_slot_size - slot.student_size) > open_slot_size:
                open_slot_size = (topic.max_slot_size - slot.student_size)
                open_slot_id = slot.slot_id
        return open_slot_size, open_slot_id

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

    def save_to_database(self):
        global locked_assignments, locked_applications
        for _assignment in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
            _assignment.delete()
        for _assignment in self.assignments.values():
            for slot in _assignment:
                assignment = Assignment.objects.get_or_create(topic=slot.topic, slot_id=slot.slot_id)[0]

                for application in slot.accepted_applications:
                    accepted_application = AcceptedApplications.objects.create(assignment=assignment,
                                                                               topic_selection=application, )
                    if application in locked_applications:
                        accepted_application.finalized_assignment = True
                        accepted_application.save()

                if (slot.topic, slot.slot_id) in locked_assignments:
                    assignment.finalized_slot = locked_assignments[(slot.topic, slot.slot_id)]
                    assignment.save()
