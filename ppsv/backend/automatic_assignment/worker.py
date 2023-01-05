import time
import django
import statistics

django.setup()


def create_assignments(strategy, topics, iteration, time_list, iterations, worker, override_assignments):
    from .assignments import Assignments
    from .applications import Applications

    assignments = Assignments(topics, override_assignments)
    _accepted_applications = []
    _applications = Applications()
    time_0 = time.time()
    for topic in strategy.get_topics(topics, iteration):
        __biggest_open_slot = assignments.biggest_open_slot(topic)
        # filter for all applications that are within this size and have this topic
        possible_applications = _applications.filter(
            lambda app: app.topic == topic and app.group.size <= __biggest_open_slot[0])
        while __biggest_open_slot[0] > 0 and len(possible_applications.values()) != 0:
            next_application = strategy.get_next_application(possible_applications, iteration)
            _applications.accept(next_application)
            assignments.add_application(next_application, __biggest_open_slot[1])
            possible_applications = _applications.filter(
                lambda app: app.topic == topic and app.group.size <= __biggest_open_slot[0])
            __biggest_open_slot = assignments.biggest_open_slot(topic)
    time_1 = time.time()
    if len(time_list) >= 100:
        time_list.pop(0)
    time_list.append(time_1 - time_0)
    print("Iteration " + str(iteration) + "/" + str(iterations) + " done in " + str(time_1 - time_0) + " with score: " + str(
        assignments.score) + ". ETA remaining: " + str(
        round(statistics.fmean(time_list) * (iterations - iteration) / worker, 2)) + " seconds")
    return assignments
