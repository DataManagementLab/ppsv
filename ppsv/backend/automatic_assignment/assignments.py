from dataclasses import dataclass

from course.models import Topic, Group
from backend.models import Assignment, possible_assignments


@dataclass
class TempAssignment:
    topic: Topic
    slot_id: int
    accepted_applications: []

    @property
    def score(self):
        score = 0
        for application in self.accepted_applications:
            score += (21 - min(10, application.priority))
        return score

    @property
    def student_size(self):
        size = 0
        for application in self.accepted_applications:
            size += application.group.size
        return size


all_assignments = {}
for assignment in Assignment.objects.all():
    accepted_applications = []
    for accepted_application in assignment.accepted_applications.all():
        accepted_applications.append(accepted_application)
    if assignment.topic not in all_assignments:
        all_assignments[assignment.topic] = []
    all_assignments[assignment.topic].append(TempAssignment(topic=assignment.topic, slot_id=assignment.slot_id,
                                                            accepted_applications=accepted_applications))

locked_assignments = all_assignments


class Assignments:
    assignments: {}

    def __init__(self, topics, override_assignments):
        self.assignments = {}
        for topic in topics:
            self.assignments[topic] = []
        self.load_assignments_from_database(override_assignments)

    def get_assignments(self, topic):
        return self.assignments.get(topic) if self.assignments.get(topic) is not None else []

    def add_application(self, application, slot_id):
        assigned = False
        for slot in self.assignments[application.topic]:
            if slot.slot_id == slot_id:
                slot.accepted_applications.append(application)
                assigned = True
        if not assigned:
            self.assignments[application.topic] = [TempAssignment(topic=application.topic, slot_id=slot_id,
                                                                  accepted_applications=[application])]

    def biggest_open_slot(self, topic):
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

    def load_assignments_from_database(self, override_assignments):
        self.assignments = locked_assignments if override_assignments else all_assignments

    @property
    def score(self):
        score = 0
        for slot in self.assignments.values():
            for assignment in slot:
                score += assignment.score
        # minus score für nicht zugewiesene gruppen?
        for group in Group.objects.all():
            for collection in group.get_collections:
                if possible_assignments(group.id, collection) == 0:
                    score -= 50
        return score

    def save_to_database(self):
        for _assignment in self.assignments.values():
            for slot in _assignment:
                assignment = Assignment.objects.get_or_create(topic=slot.topic, slot_id=slot.slot_id)[0]
                for application in slot.accepted_applications:
                    assignment.accepted_applications.add(application)
                assignment.save()
