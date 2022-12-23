from backend.models import Assignment, possible_assignments
from course.models import TopicSelection, Group, Topic


def biggest_open_slot_in_topic(topic):
    assignments = Assignment.objects.filter(topic=topic)
    if assignments.count() < topic.max_slots:
        return topic.max_slot_size, assignments.count() + 1

    biggest_open_slot_space = 0
    biggest_open_slot_id = -1
    for assignment in assignments:
        if assignment.open_places_in_slot_count > biggest_open_slot_space:
            biggest_open_slot_space = assignment.assigned_student_to_slot_count
            biggest_open_slot_id = assignment.slot_id
    return biggest_open_slot_space, biggest_open_slot_id


def filter_applications(applications, application_filter):
    filtered_applications = []
    for application in applications:
        if application_filter(application):
            filtered_applications.append(application)
    return filtered_applications


def sort_applications(applications):
    applications.sort(key=lambda app: app.priority)  # secondary key
    applications.sort(key=lambda app: possible_assignments(app.group.id, app.collection_number))  # primary key


def create_assignments():
    # Create an empty dictionary that will store the applications
    applications = {}

    # Iterate through the applications and add each application to the appropriate topic in the dictionary
    for application in TopicSelection.objects.order_by('collection_number', 'priority'):
        topic = application.topic
        if topic in applications:
            applications[topic].append(application)
        else:
            applications[topic] = [application]

    assignments = {}

    print("Creating Assignments")
    topic_counter = 1
    for topic in Topic.objects.all():
        print("Creating for Topic " + str(topic_counter) + "/" + str(Topic.objects.count()))
        topic_counter = topic_counter + 1

        if topic not in applications.keys():
            continue

        biggest_possible_application = biggest_open_slot_in_topic(topic)[0]
        while biggest_possible_application > 0:
            possible_applications = filter_applications(applications[topic],
                                                        lambda app: app.group.size <= biggest_possible_application)
            if len(possible_applications) == 0:
                break

            sort_applications(possible_applications)

            assignment = Assignment.objects.get_or_create(topic=topic, slot_id=biggest_open_slot_in_topic(topic)[1])[0]
            assignment.accepted_applications.add(possible_applications[0])
            assignment.save()
            biggest_possible_application = biggest_open_slot_in_topic(topic)[0]

    print("done")
