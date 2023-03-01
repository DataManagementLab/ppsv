import math
import time

from course.models import Topic
from .applications import Applications, init_applications
from .assignments import Assignments, init_assignments
from .strategy import Strategy

iterations = 100
running = False
progress = 0
eta = ""


def main(override_assignments):
    """the main algorithm for automatically assigning. If override_assignments is True all non-locked assignments could
    be overwritten by the algorithm. The higher iterations the better the result"""
    print("Starting automatic assignments!")
    global running, progress, eta
    progress = 0
    running = True

    # --- init --- #
    strategy = Strategy()
    time_track = 0
    init_assignments(False)
    init_applications(False)
    topics = []
    for topic in Topic.objects.all():
        topics.append(topic)

    # --- main loop --- #
    iteration = 0
    best_assignments = Assignments()
    best_assignments_score = best_assignments.score(Applications())
    if len(Applications().applications_for_topic) == 0:
        print("No possible applications possible. Canceling automatic assignments")
        return

    print("Initial Score: " + str(best_assignments_score))

    init_assignments(override_assignments)
    init_applications(override_assignments)

    while iteration < iterations:
        time0 = time.time()
        assignments = Assignments()
        applications = Applications()
        topics = strategy.get_topics(topics)
        time1 = time.time()
        print("Initializing iteration took " + str(round(time1 - time0, 2)) + "s.")
        for topic in topics:
            biggest_open_slot = assignments.biggest_open_slot(topic)
            possible_applications = []
            for possible_application in applications.get_applications_for_topic(topic):
                if possible_application.group.size <= biggest_open_slot[0]:
                    possible_applications.append(possible_application)
            while biggest_open_slot[0] > 0 and len(possible_applications) != 0:
                next_application = strategy.get_next_application(possible_applications, iteration)
                applications.accept(next_application)
                assignments.add_application(next_application, biggest_open_slot[1])
                possible_applications = []
                for possible_application in applications.get_applications_for_topic(topic):
                    if possible_application.group.size <= biggest_open_slot[0]:
                        possible_applications.append(possible_application)
                biggest_open_slot = assignments.biggest_open_slot(topic)
            if len(applications.applications_for_topic) == 0:
                return
        time2 = time.time()
        print("Creating Assignments took " + str(round(time2 - time1, 2)) + "s.")

        new_assignments_score = assignments.score(applications)
        if new_assignments_score >= best_assignments_score:
            best_assignments = assignments
            best_assignments_score = new_assignments_score

        iteration += 1

        time3 = time.time()
        if time_track != 0:
            time_track = (time_track + (time3 - time0)) / 2
        else:
            time_track = time3 - time0

        eta = "ETA remaining: " + str(round(time_track * (iterations - iteration), 2)) + " seconds"
        print("Iteration " + str(iteration) + "/" + str(iterations) + " done in " + str(
            round(time3 - time0, 2)) + "s with score: " + str(new_assignments_score) + ". " + eta)

        progress = math.floor(iteration / iterations * 100)

    print("Finished! Saving best score " + str(best_assignments_score) + " to database")
    best_assignments.save_to_database()
    print("Saved!")
    running = False
