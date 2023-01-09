import copy
import time
from dataclasses import dataclass

from backend.models import Assignment, get_score_for_assigned, get_score_for_not_assigned
from course.models import Topic


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
            score += get_score_for_assigned(application.priority)
        return score

    @property
    def student_size(self):
        """returns how many students are in currently in this assignment(slot)"""
        size = 0
        for application in self.accepted_applications:
            size += application.group.size
        return size


all_assignments = {}


def init_assignments(override_assignments):
    """inits the assignments as is the stand of the database right now. this should be used for the whole automatic
    assignment process and not be changed. If override_assignments is True all non-locked assignments could be
    overwritten by the algorithm."""
    global all_assignments
    all_assignments = {}
    for topic in Topic.objects.all():
        all_assignments[topic] = []
    for assignment in Assignment.objects.all():
        accepted_applications = []
        for accepted_application in assignment.accepted_applications.all():
            accepted_applications.append(accepted_application)
        if assignment.locked or not override_assignments:
            all_assignments[assignment.topic].append(TempAssignment(topic=assignment.topic, slot_id=assignment.slot_id,
                                                                    accepted_applications=accepted_applications))


class Assignments:
    """Represents all assignments for this iteration
    """
    assignments: {}

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
        self.assignments[application.topic] = [TempAssignment(topic=application.topic, slot_id=slot_id,
                                                              accepted_applications=[application])]

    def biggest_open_slot(self, topic):
        """returns a tuple of (slot_size, slot_id) for the biggest open slot of the given topic. will return (0,1) if
        there are no slots or no open slots for the given topic"""
        assignments = self.get_assignments(topic)
        if len(assignments) < topic.max_slots:
            return topic.max_slot_size, len(assignments) + 1
        open_slot_size = 0
        open_slot_id = 1
        for slot in assignments:
            if (topic.max_slot_size - slot.student_size) >= open_slot_size:
                open_slot_size = (topic.max_slot_size - slot.student_size)
                open_slot_id = slot.slot_id
        return open_slot_size, open_slot_id

    def score(self, applications):
        """returns the score for the all saved assignments. will use all open applications to find collections of groups
         that are not fulfilled. These will result in negativ scoring values. The range is depending on the number of
          collections. Can return a negative value. Higher values should represent a better score"""
        time0 = time.time()
        score = 0
        for slot in self.assignments.values():
            for assignment in slot:
                score += assignment.score
        # minus score für nicht zugewiesene gruppen
        score += get_score_for_not_assigned() * len(applications.applications_for_group.keys())

        time1 = time.time()
        print("Scoring took " + str(round(time1 - time0, 2)) + "s.")
        return score

    def save_to_database(self):
        """saves this assignments to the database"""
        for _assignment in self.assignments.values():
            for slot in _assignment:
                assignment = Assignment.objects.get_or_create(topic=slot.topic, slot_id=slot.slot_id)[0]
                for application in slot.accepted_applications:
                    assignment.accepted_applications.add(application)
                assignment.save()
