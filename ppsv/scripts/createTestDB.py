import random

from course.models import *


# noinspection DuplicatedCode
def run():
    # --- CONFIG --- #
    default_course_per_term = 30
    default_topic_per_course = 5
    default_special_course_per_term = 5
    default_topic_per_special_course = 3  # this is also the amount of range of the slots (from 1 to this number)
    default_course_types = 4
    default_cp_range = (1, 12)

    default_students = 300
    # dict with collection number: amount of groups that have it
    # need at least a collection 1
    default_collections_amount = {
        1: 150,
        2: 20,
        3: 5
    }
    default_max_group_size = 5  # this is also the maximum slot size
    #  will be
    # generated for each group size
    default_group_collections_amount = {
        1: int((default_special_course_per_term * default_topic_per_special_course) / (default_max_group_size / 2)),
        2: 1
    }
    default_applications_per_student_range = (4, 8)
    default_applications_per_group_range = (1, 3)

    default_maximum_single_applications_for_group_topic_per_slot = 2

    course_types = []
    print("Creating Course Types")
    for j in range(default_course_types):
        course_types.append(CourseType.objects.create(type=f"Course Type{j}"))

    faculties = []
    print("Creating Faculties")
    for id, name in Course.COURSE_FACULTY_CHOICES:
        faculties.append(id)

    # --- STUDENTS and GROUPS --- #
    students = []

    for j in range(default_students):
        print(f"Creating Students: {j}/{default_students}\r", sep=' ', end='', flush=True)
        temp_user = User.objects.create_user(username=f'student{j}', password='1234')
        temp_student = Student.objects.create(user=temp_user,
                                              tucan_id=f"tu{j}id",
                                              firstname=f"firstname{j}",
                                              lastname=f"lastname{j}",
                                              email=f"email{j}@email.de",
                                              )
        students.append(temp_student)
    print("Creating Students: Done!                      \n")

    # --- TERM SOSE22 --- #
    sose22_term_registration_start = make_aware(datetime(2022, 3, 1, 0, 0, 0))
    sose22_term_registration_deadline = make_aware(datetime(2022, 3, 31, 23, 59, 59))
    print("Creating Term SoSe22")
    sose22 = Term.objects.create(name="SoSe22",
                                 registration_start=sose22_term_registration_start,
                                 registration_deadline=sose22_term_registration_deadline,
                                 )

    sose22_students = random.sample(students, default_collections_amount[1])
    sose22_groups = {}
    sose22_groups_multiple_students = []
    for group_size in range(1, default_max_group_size + 1):
        if group_size not in sose22_groups:
            sose22_groups[group_size] = []
        temp_amount = list(default_collections_amount.values())[0] if group_size == 1 else \
            list(default_group_collections_amount.values())[0]
        for j in range(temp_amount):
            print(f"Creating Group: {j}/{temp_amount} Step{group_size - 1}/{default_max_group_size}    \r", sep=' ',
                  end='', flush=True)
            temp_group = Group.objects.create(term=sose22)
            for student in random.sample(sose22_students, group_size):
                temp_group.students.add(student)
            temp_group.save()
            sose22_groups[group_size].append(temp_group)
            if group_size > 1:
                sose22_groups_multiple_students.append(temp_group)
    print("Creating Groups: Done!                      ")

    sose22_topics = []
    for i in range(default_course_per_term):
        print(f"Creating Courses: {i}/{default_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Course SoSe22 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=sose22,
                                            registration_start=sose22_term_registration_start,
                                            registration_deadline=sose22_term_registration_deadline,
                                            description=f"Description of Course SoSe22{i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Course SoSe22 {i}",
                                            )
        for j in range(default_topic_per_course):
            sose22_topics.append(Topic.objects.create(course=temp_course,
                                                      title=f"Topic {j} Course SoSe22 {i}",
                                                      max_slots=1,
                                                      min_slot_size=1,
                                                      max_slot_size=1,
                                                      description=f"Description of Topic {j} Course SoSe22 {j}"
                                                      ))
    print("Creating Courses: Done!                      ")

    sose22_group_topics = {}
    for i in range(default_special_course_per_term):
        print(f"Creating special Courses: {i}/{default_special_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Special Course SoSe22 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=sose22,
                                            registration_start=sose22_term_registration_start,
                                            registration_deadline=sose22_term_registration_deadline,
                                            description=f"Description of Special Course SoSe22 {i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Special Course SoSe22 {i}",
                                            )

        for j in range(default_topic_per_special_course):
            temp_max_slot_size = random.randint(1, default_max_group_size)
            temp_min_slot_size = random.randint(1, temp_max_slot_size)

            temp_topic = Topic.objects.create(course=temp_course,
                                              title=f"Topic {j} Special Course SoSe22 {i}",
                                              max_slots=j + 1,
                                              min_slot_size=temp_min_slot_size,
                                              max_slot_size=temp_max_slot_size,
                                              description=f"Description of Topic {j} Special Course SoSe22 {j}"
                                              )
            sose22_topics.append(temp_topic)
            for k in range(2, temp_max_slot_size + 1):
                if k not in sose22_group_topics:
                    sose22_group_topics[k] = []
                sose22_group_topics[k].append(temp_topic)
    print("Creating special Courses: Done!                      ")

    # --- APPLICATIONS TERM SOSE22 --- #
    sose22_groups_of_topic = {}

    temp_groups_multiple_collections = {1: sose22_groups[1]}
    temp_max_collection_id = list(default_collections_amount.keys())[-1]
    for collection_id, amount in default_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    for collection_id, amount in default_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating single applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            for j, topic in enumerate(random.sample(
                    sose22_topics,
                    random.randint(default_applications_per_student_range[0],
                                   default_applications_per_student_range[1] + 1))):

                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)
                if topic not in sose22_groups_of_topic:
                    sose22_groups_of_topic[topic] = []
                sose22_groups_of_topic[topic].extend(group.students.all())

                if topic.max_slot_size > 1 and len(
                        sose22_groups_of_topic[topic]) == default_maximum_single_applications_for_group_topic_per_slot:
                    sose22_topics.remove(topic)
    print("Creating default Applications for Group: Done!                      ")

    temp_groups_multiple_collections = {1: sose22_groups_multiple_students}
    for collection_id, amount in default_group_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    temp_max_collection_id = list(default_group_collections_amount.keys())[-1]
    for collection_id, amount in default_group_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating group applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            if group.size not in sose22_group_topics:
                continue
            for j, topic in enumerate(random.sample(sose22_group_topics[group.size],
                                                    min(len(sose22_group_topics[group.size]),
                                                        random.randint(default_applications_per_group_range[0],
                                                                       default_applications_per_group_range[
                                                                           1] + 1)))):
                if topic not in sose22_groups_of_topic:
                    sose22_groups_of_topic[topic] = []
                if any(student in group.students.all() for student in sose22_groups_of_topic[topic]):
                    break
                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)

                sose22_groups_of_topic[topic].extend(group.students.all())
    print("Creating special Applications for Group: Done!                      \n")

    # --- TERM WISE22/23 --- #

    wise22_term_registration_start = make_aware(datetime(2022, 11, 1, 0, 0, 0))
    wise22_term_registration_deadline = make_aware(datetime(2022, 11, 30, 23, 59, 59))
    print("Creating Term WiSe22")
    wise22 = Term.objects.create(name="WiSe22",
                                 registration_start=wise22_term_registration_start,
                                 registration_deadline=wise22_term_registration_deadline, )
    wise22_students = random.sample(students, default_collections_amount[1])
    wise22_groups = {}
    wise22_groups_multiple_students = []
    for group_size in range(1, default_max_group_size + 1):
        if group_size not in wise22_groups:
            wise22_groups[group_size] = []
        temp_amount = list(default_collections_amount.values())[0] if group_size == 1 else \
            list(default_group_collections_amount.values())[0]
        for j in range(temp_amount):
            print(f"Creating Group: {j}/{temp_amount} Step{group_size - 1}/{default_max_group_size}    \r", sep=' ',
                  end='', flush=True)
            temp_group = Group.objects.create(term=wise22)
            for student in random.sample(wise22_students, group_size):
                temp_group.students.add(student)
            temp_group.save()
            wise22_groups[group_size].append(temp_group)
            if group_size > 1:
                wise22_groups_multiple_students.append(temp_group)
    print("Creating Groups: Done!                      ")

    wise22_topics = []
    for i in range(default_course_per_term):
        print(f"Creating Courses: {i}/{default_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Course WiSe22 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=wise22,
                                            registration_start=wise22_term_registration_start,
                                            registration_deadline=wise22_term_registration_deadline,
                                            description=f"Description of Course WiSe22 {i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Course WiSe22 {i}",
                                            )
        for j in range(default_topic_per_course):
            wise22_topics.append(Topic.objects.create(course=temp_course,
                                                      title=f"Topic {j} Course WiSe22 {i}",
                                                      max_slots=1,
                                                      min_slot_size=1,
                                                      max_slot_size=1,
                                                      description=f"Description of Topic {j} Course WiSe22 {j}"
                                                      ))
    print("Creating Courses: Done!                      ")

    wise22_group_topics = {}
    for i in range(default_special_course_per_term):
        print(f"Creating special Courses: {i}/{default_special_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Special Course wise22 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=wise22,
                                            registration_start=wise22_term_registration_start,
                                            registration_deadline=wise22_term_registration_deadline,
                                            description=f"Description of Special Course wise22 {i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Special Course wise22 {i}",
                                            )

        for j in range(default_topic_per_special_course):
            temp_max_slot_size = random.randint(1, default_max_group_size)
            temp_min_slot_size = random.randint(1, temp_max_slot_size)

            temp_topic = Topic.objects.create(course=temp_course,
                                              title=f"Topic {j} Special Course wise22 {i}",
                                              max_slots=j + 1,
                                              min_slot_size=temp_min_slot_size,
                                              max_slot_size=temp_max_slot_size,
                                              description=f"Description of Topic {j} Special Course wise22 {j}"
                                              )
            wise22_topics.append(temp_topic)
            for k in range(2, temp_max_slot_size + 1):
                if k not in wise22_group_topics:
                    wise22_group_topics[k] = []
                wise22_group_topics[k].append(temp_topic)
    print("Creating special Courses: Done!                      ")

    # --- APPLICATIONS TERM WISE22 --- #

    wise22_groups_of_topic = {}

    temp_groups_multiple_collections = {1: wise22_groups[1]}
    temp_max_collection_id = list(default_collections_amount.keys())[-1]
    for collection_id, amount in default_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    for collection_id, amount in default_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating single applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            for j, topic in enumerate(random.sample(
                    wise22_topics,
                    random.randint(default_applications_per_student_range[0],
                                   default_applications_per_student_range[1] + 1))):

                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)
                if topic not in wise22_groups_of_topic:
                    wise22_groups_of_topic[topic] = []
                wise22_groups_of_topic[topic].extend(group.students.all())

                if topic.max_slot_size > 1 and len(
                        wise22_groups_of_topic[topic]) == default_maximum_single_applications_for_group_topic_per_slot:
                    wise22_topics.remove(topic)
    print("Creating default Applications for Group: Done!                      ")

    temp_groups_multiple_collections = {1: wise22_groups_multiple_students}
    for collection_id, amount in default_group_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    temp_max_collection_id = list(default_group_collections_amount.keys())[-1]
    for collection_id, amount in default_group_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating group applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            if group.size not in wise22_group_topics:
                continue
            for j, topic in enumerate(random.sample(wise22_group_topics[group.size],
                                                    min(len(wise22_group_topics[group.size]),
                                                        random.randint(default_applications_per_group_range[0],
                                                                       default_applications_per_group_range[
                                                                           1] + 1)))):
                if topic not in wise22_groups_of_topic:
                    wise22_groups_of_topic[topic] = []
                if any(student in group.students.all() for student in wise22_groups_of_topic[topic]):
                    break
                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)
                wise22_groups_of_topic[topic].extend(group.students.all())
    print("Creating special Applications for Group: Done!                      \n")

    # --- TERM SOSE23 --- #

    sose23_term_registration_start = make_aware(datetime(2023, 1, 1, 0, 0, 0))
    sose23_term_registration_deadline = make_aware(datetime(2023, 5, 31, 23, 59, 59))
    print("Creating Term SoSe23")
    sose23 = Term.objects.create(name="SoSe23",
                                 registration_start=sose23_term_registration_start,
                                 registration_deadline=sose23_term_registration_deadline,
                                 active_term=True)
    sose23_students = random.sample(students, default_collections_amount[1])
    sose23_groups = {}
    sose23_groups_multiple_students = []
    for group_size in range(1, default_max_group_size + 1):
        if group_size not in sose23_groups:
            sose23_groups[group_size] = []
        temp_amount = list(default_collections_amount.values())[0] if group_size == 1 else \
            list(default_group_collections_amount.values())[0]
        for j in range(temp_amount):
            print(f"Creating Group: {j}/{temp_amount} Step{group_size - 1}/{default_max_group_size}    \r", sep=' ',
                  end='', flush=True)
            temp_group = Group.objects.create(term=sose23)
            for student in random.sample(sose23_students, group_size):
                temp_group.students.add(student)
            temp_group.save()
            sose23_groups[group_size].append(temp_group)
            if group_size > 1:
                sose23_groups_multiple_students.append(temp_group)
    print("Creating Groups: Done!                      ")

    sose23_topics = []
    for i in range(default_course_per_term):
        print(f"Creating Courses: {i}/{default_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Course sose23 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=sose23,
                                            registration_start=sose23_term_registration_start,
                                            registration_deadline=sose23_term_registration_deadline,
                                            description=f"Description of Course sose23 {i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Course sose23 {i}",
                                            )
        for j in range(default_topic_per_course):
            sose23_topics.append(Topic.objects.create(course=temp_course,
                                                      title=f"Topic {j} Course sose23 {i}",
                                                      max_slots=1,
                                                      min_slot_size=1,
                                                      max_slot_size=1,
                                                      description=f"Description of Topic {j} Course sose23 {j}"
                                                      ))
    print("Creating Courses: Done!                      ")

    sose23_group_topics = {}
    for i in range(default_special_course_per_term):
        print(f"Creating special Courses: {i}/{default_special_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Special Course sose23 {i}",
                                            type=course_types[i % len(course_types)],
                                            term=sose23,
                                            registration_start=sose23_term_registration_start,
                                            registration_deadline=sose23_term_registration_deadline,
                                            description=f"Description of Special Course sose23 {i}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[i % len(faculties)],
                                            organizer=f"Organizer of Special Course sose23 {i}",
                                            )

        for j in range(default_topic_per_special_course):
            temp_max_slot_size = random.randint(1, default_max_group_size)
            temp_min_slot_size = random.randint(1, temp_max_slot_size)

            temp_topic = Topic.objects.create(course=temp_course,
                                              title=f"Topic {j} Special Course sose23 {i}",
                                              max_slots=j + 1,
                                              min_slot_size=temp_min_slot_size,
                                              max_slot_size=temp_max_slot_size,
                                              description=f"Description of Topic {j} Special Course sose23 {j}"
                                              )
            sose23_topics.append(temp_topic)
            for k in range(2, temp_max_slot_size + 1):
                if k not in sose23_group_topics:
                    sose23_group_topics[k] = []
                sose23_group_topics[k].append(temp_topic)
    print("Creating special Courses: Done!                      ")

    # --- APPLICATIONS TERM sose23 --- #

    sose23_groups_of_topic = {}

    temp_groups_multiple_collections = {1: sose23_groups[1]}
    temp_max_collection_id = list(default_collections_amount.keys())[-1]
    for collection_id, amount in default_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    for collection_id, amount in default_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating single applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            for j, topic in enumerate(random.sample(
                    sose23_topics,
                    random.randint(default_applications_per_student_range[0],
                                   default_applications_per_student_range[1] + 1))):

                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)
                if topic not in sose23_groups_of_topic:
                    sose23_groups_of_topic[topic] = []
                sose23_groups_of_topic[topic].extend(group.students.all())

                if topic.max_slot_size > 1 and len(
                        sose23_groups_of_topic[topic]) == default_maximum_single_applications_for_group_topic_per_slot:
                    sose23_topics.remove(topic)
    print("Creating default Applications for Group: Done!                      ")

    temp_groups_multiple_collections = {1: sose23_groups_multiple_students}
    for collection_id, amount in default_group_collections_amount.items():
        if collection_id > 1:
            temp_groups_multiple_collections[collection_id] = random.sample(
                temp_groups_multiple_collections[collection_id - 1], amount)
    temp_max_collection_id = list(default_group_collections_amount.keys())[-1]
    for collection_id, amount in default_group_collections_amount.items():
        for i, group in enumerate(temp_groups_multiple_collections[collection_id]):
            print(
                f"Creating group applications for Group: {i}/{amount} Step {collection_id}/{temp_max_collection_id}     \r",
                sep=' ', end='', flush=True)
            if group.size not in sose23_group_topics:
                continue
            for j, topic in enumerate(random.sample(sose23_group_topics[group.size],
                                                    min(len(sose23_group_topics[group.size]),
                                                        random.randint(default_applications_per_group_range[0],
                                                                       default_applications_per_group_range[
                                                                           1] + 1)))):
                if topic not in sose23_groups_of_topic:
                    sose23_groups_of_topic[topic] = []
                if any(student in group.students.all() for student in sose23_groups_of_topic[topic]):
                    break
                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1,
                                              collection_number=collection_id)
                sose23_groups_of_topic[topic].extend(group.students.all())
    print("Creating special Applications for Group: Done!                      ")

    print("\nFinished Creating DB!")
