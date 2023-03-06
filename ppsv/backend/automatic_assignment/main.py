import cProfile
import itertools
import statistics
import time
import traceback

from course.models import Topic, Term, TopicSelection
from .applications import Applications, init_applications
from .assignments import Assignments, init_assignments, topic_data
from .strategy import Strategy
from ..models import Assignment, AcceptedApplications, TermFinalization
from ..pages.functions import get_score_for_assigned, get_score_for_not_assigned

iterations = 10000
running = False
progress = 0.0
eta = ""


def start_algo(override_assignments):
    if TermFinalization.is_finalized(Term.get_active_term()):
        raise ValueError("This Term is locked.")
    global running, progress, eta
    progress = 0.0
    running = True
    eta = "Initializing"
    try:
        profiler = cProfile.Profile()
        profiler.enable()
        main(override_assignments)
        profiler.disable()
        profiler.dump_stats('py automatic_assignment.prof')
    except Exception as e:
        progress = 0.0
        running = False
        print(traceback.format_exc())
        raise e
    progress = 0.0
    running = False
    eta = ""


def get_database_score():
    score = 0

    for assignment in Assignment.objects.filter(topic__course__term=Term.get_active_term()):
        for application in assignment.accepted_applications.all():
            score += get_score_for_assigned(application.group.size, application.priority)

    handled_apps = list(AcceptedApplications.get_collection_dict().keys())
    for application in TopicSelection.objects.filter(topic__course__term=Term.get_active_term()):
        if application.dict_key not in handled_apps:
            handled_apps.append(application.dict_key)
            score += get_score_for_not_assigned()

    return score


def main(override_assignments):
    """the main algorithm for automatically assigning. If override_assignments is True all non-locked assignments could
    be overwritten by the algorithm. The higher iterations the better the result"""
    print("Starting automatic assignments!")
    global eta, progress

    # --- init --- #
    time_track = None
    topic_ids = [elem[0] for elem in (Topic.objects.filter(course__term=Term.get_active_term()).values_list('pk'))]
    strategy = Strategy()
    iteration = 0
    best_assignments_score = get_database_score()
    max_assignments_score = get_max_score()

    print("Initial Score: " + str(best_assignments_score))
    init_assignments(override_assignments)
    init_applications(override_assignments)
    term = Term.get_active_term()

    best_assignments = None

    if len(Applications().applications_for_group) == 0:
        print("No possible applications possible. Canceling automatic assignments")
        return

    # --- main loop --- #
    while iteration < iterations:
        if best_assignments_score == max_assignments_score:
            print("Perfect Scoring! Stopping Algorithm")
            break

        time0 = round(time.time() * 1000)
        assignments, applications = do_iteration(strategy, topic_ids)
        iteration += 1
        new_assignments_score = assignments.score(applications)
        if new_assignments_score >= best_assignments_score:
            best_assignments = assignments
            best_assignments_score = new_assignments_score

        strategy.next_iteration(new_assignments_score >= best_assignments_score, new_assignments_score)

        time3 = round(time.time() * 1000)
        if time_track is None:
            time_track = [(time3 - time0) for _ in range(100)]
        time_track[iteration % 100] = (time3 - time0)
        it_time_mean = statistics.mean(time_track)
        eta = "ETA remaining: {0} ({5}ms). Score: {1}/{2}/{3}. Override: {4}".format(
            print_time(it_time_mean * (iterations - iteration)),
            new_assignments_score,
            best_assignments_score,
            max_assignments_score,
            override_assignments,
            it_time_mean
        )
        progress = round(iteration / iterations * 100, 2)

        # print(
        #     "Automatic Assignment running: {:.2f}% ".format(progress) + str(eta) + " took " + str(time3 - time0) + "ms")

    if best_assignments is not None and best_assignments_score > get_database_score():
        print("Saving to database")
        best_assignments.save_to_database(term)
    else:
        print("No better assignments found! Not saving to database")


def do_iteration(strategy, topic_ids):
    assignments = Assignments()
    applications = Applications()
    topic_ids = strategy.get_topics(topic_ids)

    for topic_id in topic_ids:
        if topic_data[topic_id].min_slot_size > 1:
            for slot_id in range(1, topic_data[topic_id].slots + 1):
                possible_applications = get_possible_applications_for_slot(applications, assignments, topic_id, slot_id)
                if len(possible_applications) == 0:
                    break
                create_group_topic_assignment(applications,
                                              possible_applications,
                                              strategy,
                                              topic_id,
                                              assignments,
                                              slot_id,
                                              assignments.get_remaining_space_in_slot(topic_id, slot_id))
        else:
            for slot_id in range(1, topic_data[topic_id].slots + 1):
                possible_applications = get_possible_applications_for_slot(applications, assignments, topic_id, slot_id)
                if len(possible_applications) == 0:
                    break
                create_single_topic_assignment(applications,
                                               possible_applications,
                                               strategy,
                                               topic_id,
                                               assignments,
                                               slot_id)

    return assignments, applications


def get_possible_applications_for_slot(applications, assignments, topic_id, slot_id):
    return applications.get_applications_for_topic_with_max_size(topic_id,
                                                                 assignments.get_remaining_space_in_slot(topic_id,
                                                                                                         slot_id))


def create_group_topic_assignment(applications, possible_applications, strategy, topic_id, assignments, slot,
                                  remaining_slot_space):
    """creates a group assignment. returns false if it was not successful"""
    group_application = []
    possible = False
    application_size = 0

    while application_size < remaining_slot_space:
        # no applications possible so we need to stop with this permutation
        possible = topic_data[topic_id].min_slot_size <= application_size
        if len(possible_applications) == 0:
            break
        application = strategy.get_next_application(topic_id, possible_applications)
        application_size += application.size
        group_application.append(application)
        possible_applications = [application for application in
                                 applications.get_applications_for_topic_with_max_size(
                                     topic_id,
                                     remaining_slot_space - application_size)
                                 if application not in group_application]
    # found sth that works, we will stop looking at other permutations.
    if possible:
        for application in group_application:
            applications.accept(application)
            assignments.add_application(application, slot)

    return possible


def create_single_topic_assignment(applications, possible_applications, strategy, topic_id, assignments, slot):
    application = strategy.get_next_application(topic_id, possible_applications)
    possible_applications.remove(application)
    applications.accept(application)
    assignments.add_application(application, slot)


def print_time(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    return "%d:%d:%d" % (hours, minutes, seconds)


def get_max_score():
    """
    :return: Returns the highest possible score when considering the current applications
    :rtype: int
    """
    handled_applications = []
    score = 0
    for application in TopicSelection.objects.filter(topic__course__term=Term.get_active_term()):
        if (application.group, application.collection_number) not in handled_applications:
            handled_applications.append((application.group, application.collection_number))
            score += get_score_for_assigned(application.group.size, 1)
    return score
