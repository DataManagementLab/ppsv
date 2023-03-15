from dataclasses import dataclass

from backend.pages.functions import get_score_for_assigned
from course.models import Topic


@dataclass
class TempAssignment:
    """This class represents one temporary assignment for this iteration"""
    topic_id: int
    slot_id: int
    accepted_applications: []
    locked: int

    @property
    def score(self):
        """returns the score of this assignment in range [20,10], while 20 will be given for an application with
        priority 1, 19 for priority 2 and so on"""
        score = 0
        for application in self.accepted_applications:
            score += get_score_for_assigned(application.size, application.priority)
        return score

    @property
    def size(self):
        """returns how many students are in currently in this assignment(slot)"""
        size = 0
        for application in self.accepted_applications:
            size += application.size
        return size


@dataclass
class TempApplication:
    """This class represents one temporary application for this iteration"""
    id: int
    size: int
    priority: int
    locked: bool
    topic_id: int
    collection_id: int
    group_id: int

    @property
    def score(self):
        """returns the score of this assignment"""
        return get_score_for_assigned(self.size, self.priority)

    @property
    def dict_key(self):
        return self.group_id, self.collection_id


@dataclass
class TempTopic:
    slots: int
    min_slot_size: int
    max_slot_size: int
    topic: Topic
