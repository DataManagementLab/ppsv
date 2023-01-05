import multiprocessing
import traceback

from course.models import Topic
from concurrent.futures import ProcessPoolExecutor, as_completed
from .worker import create_assignments
from .strategy import Strategy
from .assignments import Assignments

iterations = 100
workers = 4


def main(override_assignments):
    print("Starting automatic assignments!")

    # --- init --- #
    strategy = Strategy()
    time_list = multiprocessing.Manager().list()
    topics = []
    for topic in Topic.objects.all():
        if topic.has_applications:
            topics.append(topic)
    # --- main loop --- #
    best_assignments = Assignments(topics, False)
    print("Initial Score: " + str(best_assignments.score))

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = []
        for iteration in range(iterations):
            futures.append(
                executor.submit(create_assignments, strategy, topics, iteration, time_list, iterations, workers,
                                override_assignments))
        print("created all iterations.")
        for future in as_completed(futures):
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s: %s' % (future, exc, full_stack()))
            else:
                if best_assignments.score < data.score:
                    best_assignments = data

    print("Finished! Saving best score " + str(best_assignments.score) + " to database")
    best_assignments.save_to_database()
    print("Saved!")

def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

