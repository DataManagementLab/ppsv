import random


class Strategy:
    """The strategy in which applications and topics will be iterated."""
    seed: int

    def __init__(self):
        self.iteration = 0
        self.seed = random.randint(0, 256)

    def get_next_application(self, applications, iteration):
        """returns the next application from the given applications based on the iteration"""
        return applications.pop((iteration + random.randint(0, self.seed)) % len(applications))

    def get_topics(self, topics):
        """returns the list of topics for one iteration"""
        random.shuffle(topics)
        return topics
