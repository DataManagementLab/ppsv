import random


class Strategy:
    seed: int

    def __init__(self):
        self.iteration = 0
        self.seed = random.randint(0, 256)

    def get_next_application(self, possible_applications, iteration):
        applications = []
        for possible_application in possible_applications.values():
            applications.append(possible_application[0])

        return applications.pop((iteration + random.randint(0, self.seed)) % len(applications))

    def get_topics(self, topics, iteration):
        random.shuffle(topics)
        return topics
