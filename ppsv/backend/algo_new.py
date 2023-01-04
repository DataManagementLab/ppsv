from dataclasses import dataclass
import random

from backend.models import Assignment, possible_assignments
from course.models import Group, TopicSelection, Topic


def main():
    print("Starting automatic assignments!")

    # --- init --- #
    max_number_of_iterations = 1
    strategy = Strategy()

    topics = []
    for topic in Topic.objects.all():
        if topic.has_applications:
            topics.append(topic)

    # --- main loop --- #
    iteration = 0
    best_assignments = Assignments(topics)
    print("Initial Score: " + str(best_assignments.score))
    while iteration < max_number_of_iterations:
        _assignments = Assignments(topics)
        _accepted_applications = []
        _applications = Applications(topics)

        for topic in topics:
            __biggest_open_slot = _assignments.biggest_open_slot(topic)
            # filter for all applications that are within this size
            possible_applications = _applications.filter(
                lambda app: app.topic == topic and app.group.size <= __biggest_open_slot[0])
            while __biggest_open_slot[0] > 0 and len(possible_applications.values()) != 0:
                next_application = strategy.get_next_application(possible_applications)
                _applications.accept(next_application)
                _assignments.add_application(next_application, __biggest_open_slot[1])
                possible_applications = _applications.filter(
                    lambda app: app.topic == topic and app.group.size <= __biggest_open_slot[0])
                __biggest_open_slot = _assignments.biggest_open_slot(topic)

        print("Iteration " + str(iteration) + " done with score: " + str(_assignments.score))

        if _assignments.score >= best_assignments.score:
            best_assignments = _assignments

        iteration += 1
        strategy.iteration += 1

    best_assignments.save_to_database()


class Assignments:
    assignments: {}

    def __init__(self, topics):
        self.assignments = {}
        for topic in topics:
            self.assignments[topic] = []
        self.load_assignments_from_database()

    def get_assignments(self, topic):
        return self.assignments.get(topic)

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

    def load_assignments_from_database(self):
        for assignment in Assignment.objects.all():
            accepted_applications = []
            for accepted_application in assignment.accepted_applications.all():
                accepted_applications.append(accepted_application)
            self.assignments[assignment.topic].append(
                TempAssignment(topic=assignment.topic, slot_id=assignment.slot_id,
                               accepted_applications=accepted_applications))

    @property
    def score(self):
        score = 0
        for slot in self.assignments.values():
            for assignment in slot:
                score += assignment.score
        # minus score für nicht zugewiesene gruppen?
        return score

    def save_to_database(self):
        for _assignment in self.assignments.values():
            for slot in _assignment:
                assignment = Assignment.objects.get_or_create(topic=slot.topic, slot_id=slot.slot_id)[0]
                for application in slot.accepted_applications:
                    assignment.accepted_applications.add(application)
                assignment.save()


@dataclass
class TempAssignment:
    topic: Topic
    slot_id: int
    accepted_applications: []

    @property
    def score(self):
        score = 0
        for application in self.accepted_applications:
            score += (21 - application.priority)
        return score

    @property
    def student_size(self):
        size = 0
        for application in self.accepted_applications:
            size += application.group.size
        return size


class Applications:
    applications: []

    def __init__(self, topics):
        self.applications = []
        self.load_applications_from_database(topics)

    def add(self, application):
        self.applications.append(application)

    def accept(self, application):
        """If we accept we will also remove all applications from this group and collection"""
        for _application in self.applications:
            if _application.group == application.group and \
                    _application.collection_number == application.collection_number:
                self.applications.remove(_application)

    def get_applications_for_topic(self, topic):
        applications = []
        for application in self.applications:
            if application.topic == topic:
                applications.append(application)
        return applications

    def load_applications_from_database(self, topics):
        accepted_applications = []
        for assignment in Assignment.objects.all():
            if assignment.topic in topics:
                for accepted_application in assignment.accepted_applications.all():
                    accepted_applications.append((accepted_application.group, accepted_application.collection_number))
        for application in TopicSelection.objects.all():
            if not (application.group, application.collection_number) in accepted_applications:
                self.applications.append(application)

    def has_topic(self, topic):
        for application in self.applications:
            if application.topic == topic:
                return True
        return False

    def filter(self, predicate):
        applications = {}
        for application in self.applications:
            if predicate(application):
                if (application.group, application.collection_number) not in applications:
                    applications[(application.group, application.collection_number)] = []
                applications[(application.group, application.collection_number)].append(application)
        return applications


class Strategy:
    iteration: int
    seed: int

    def __init__(self):
        self.iteration = 0
        self.seed = random.randint(0, 256)

    def get_next_application(self, possible_applications):
        applications = []
        for possible_application in possible_applications.values():
            applications.append(possible_application[0])

        return applications.pop((self.iteration + random.randint(0, self.seed)) % len(applications))
