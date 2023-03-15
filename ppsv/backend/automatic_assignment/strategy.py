import math
import random


class Strategy:
    """The strategy in which applications and topics will be iterated."""

    def __init__(self):
        self.iteration = 0
        self.seed = random.randint(0, 256)
        # self.seed = -1
        self.mutation_rate = 0.05
        self.mutation_cycle = 5
        self.mutation_cycle_rate = 0.5
        self.topic_list_mutation_cycle = self.mutation_cycle * 2
        self._topic_cycle_order = {}
        self.application_order = {}
        self.application_order_index = {}
        self.topic_cycle = 0

    @property
    def topic_cycle_order(self):
        """a map with topics as key and list of applications as values"""
        if self.topic_cycle not in self._topic_cycle_order:
            self._topic_cycle_order[self.topic_cycle] = {}
        return self._topic_cycle_order[self.topic_cycle]

    def get_next_application(self, topic, applications):
        """returns the next application from the given applications based on the iteration"""
        if topic not in self.topic_cycle_order:
            if self.iteration % self.mutation_cycle == 0:
                application = applications[0]
            else:
                application = self.get_random_application(applications)
        else:
            if topic not in self.application_order_index:
                self.application_order_index[topic] = 0
            if self.iteration % self.mutation_cycle == 0:
                application = self.get_mutation_application(topic, applications, self.mutation_cycle_rate)
            else:
                application = self.get_mutation_application(topic, applications, self.mutation_rate)

        if topic not in self.application_order:
            self.application_order[topic] = []
        self.application_order[topic].append(application)

        return application

    def get_random_application(self, applications):
        return applications[(self.iteration + self.seed) % len(applications)]

    def get_mutation_application(self, topic, applications, mutation_rate):
        if random.random() > mutation_rate:
            # dont mutate
            # check if we have elements left in saved order, otherwise return a random one
            if self.application_order_index[topic] >= len(self.topic_cycle_order[topic]):
                return self.get_random_application(applications)

            # get possible indices
            possible_indices = [i for i in
                                range(self.application_order_index[topic], len(self.topic_cycle_order[topic]))]
            for possible_index in possible_indices:
                if self.topic_cycle_order[topic][possible_index] in applications:
                    return self.topic_cycle_order[topic][possible_index]

            application = self.topic_cycle_order[topic][self.application_order_index[topic]]
            self.application_order_index[topic] += 1
            while application not in applications:
                if self.application_order_index[topic] >= len(self.topic_cycle_order[topic]):
                    return self.get_random_application(applications)
                application = self.topic_cycle_order[topic][self.application_order_index[topic]]
                self.application_order_index[topic] += 1
            return application
        else:
            # mutate
            return self.get_random_application(applications)

    def get_topics(self, topics):
        """returns the list of topics for one iteration"""
        if self.seed == -1:
            return topics
        if self.iteration % self.topic_list_mutation_cycle == 0:
            random.shuffle(topics)

        return topics

    def next_iteration(self, iteration_better, score):
        if iteration_better or len(self._topic_cycle_order[self.topic_cycle]) == 0:
            self._topic_cycle_order[self.topic_cycle] = self.application_order
            # if math.floor(self.iteration / self.topic_list_mutation_cycle) not in self.score_for_topic_cycle:
            #     self.score_for_topic_cycle[math.floor(self.iteration / self.topic_list_mutation_cycle)] = []
            # self.score_for_topic_cycle[math.floor(self.iteration / self.topic_list_mutation_cycle)] = score

        self.application_order = {}
        self.application_order_index = {}
        self.iteration += 1

        # print("getting applications took " + str(round(self.time * 1000)) + "ms")

        if self.iteration % self.topic_list_mutation_cycle == 0:
            self.topic_cycle = math.floor(self.iteration / self.topic_list_mutation_cycle)

    def topic_cycle(self, value):
        self.topic_cycle = value
