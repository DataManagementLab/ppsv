import random

from course.models import *
from backend.models import *
from datetime import datetime
from django.utils.timezone import make_aware


# noinspection DuplicatedCode
def run():
    # --- CONFIG --- #
    default_course_per_term = 30
    default_topic_per_course = 5
    default_max_group_size = 5
    default_special_course_per_term = 5
    default_topic_per_special_course = 3
    default_course_types = 4
    default_students = 100  # should be somewhat in the range of default_course_per_term * default_topic_per_course
    default_cp_range = (1, 12)
    default_applications_per_student_range = (4, 8)
    default_applications_per_group_range = (1, 3)

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
    groups = {1: []}

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
        temp_group = Group.objects.create()
        temp_group.students.add(temp_student)
        temp_group.save()
        groups[1].append(temp_group)
    print("Creating Students: Done!                      \n")

    groups_per_group_size = int(
        default_special_course_per_term * default_topic_per_special_course * 1.5 / default_max_group_size)
    for group_size in range(2, default_max_group_size + 1):
        print(f"Creating Group with size{group_size}: {group_size - 2}/{default_max_group_size - 1}\r", sep=' ', end='',
              flush=True)
        if group_size not in groups:
            groups[group_size] = []
        for j in range(groups_per_group_size):
            temp_group = Group.objects.create()
            for student in random.sample(students, group_size):
                temp_group.students.add(student)
            temp_group.save()
            groups[group_size].append(temp_group)
    print("Creating Groups: Done!                      ")

    # --- TERM SOSE22 --- #

    sose22_term_registration_start = make_aware(datetime(2022, 3, 1, 0, 0, 0))
    sose22_term_registration_deadline = make_aware(datetime(2022, 3, 31, 23, 59, 59))
    print("Creating Term SoSe22")
    sose22 = Term.objects.create(name="SoSe22",
                                 registration_start=sose22_term_registration_start,
                                 registration_deadline=sose22_term_registration_deadline,
                                 active_term=True)
    sose22_topics = []
    sose22_special_topics = {}
    for j in range(default_course_per_term):
        print(f"Creating Courses: {j}/{default_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Course SoSe22 {j}",
                                            type=course_types[j % len(course_types)],
                                            term=sose22,
                                            registration_start=sose22_term_registration_start,
                                            registration_deadline=sose22_term_registration_deadline,
                                            description=f"Description of Course SoSe22{j}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[j % len(faculties)],
                                            organizer=f"Organizer of Course SoSe22 {j}",
                                            )
        for j in range(default_topic_per_course):
            sose22_topics.append(Topic.objects.create(course=temp_course,
                                                      title=f"Topic {j} Course SoSe22 {j}",
                                                      max_slots=1,
                                                      min_slot_size=1,
                                                      max_slot_size=1,
                                                      description=f"Description of Topic {j} Course SoSe22 {j}"
                                                      ))
    print("Creating Courses: Done!                      ")

    for j in range(default_special_course_per_term):
        print(f"Creating special Courses: {j}/{default_special_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Special Course SoSe22 {j}",
                                            type=course_types[j % len(course_types)],
                                            term=sose22,
                                            registration_start=sose22_term_registration_start,
                                            registration_deadline=sose22_term_registration_deadline,
                                            description=f"Description of Special Course SoSe22 {j}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[j % len(faculties)],
                                            organizer=f"Organizer of Special Course SoSe22 {j}",
                                            )

        for j in range(default_topic_per_special_course):
            temp_max_slot_size = random.randint(1, default_max_group_size)
            temp_min_slot_size = random.randint(1, temp_max_slot_size)

            temp_topic = Topic.objects.create(course=temp_course,
                                              title=f"Topic {j} Special Course SoSe22 {j}",
                                              max_slots=j + 1,
                                              min_slot_size=temp_min_slot_size,
                                              max_slot_size=temp_max_slot_size,
                                              description=f"Description of Topic {j} Special Course SoSe22 {j}"
                                              )
            sose22_topics.append(temp_topic)
            for k in range(2, temp_max_slot_size + 1):
                if k not in sose22_special_topics:
                    sose22_special_topics[k] = []
                sose22_special_topics[k].append(temp_topic)
    print("Creating special Courses: Done!                      ")

    # --- APPLICATIONS TERM SOSE22 --- #

    # TODO multiple collections
    students_of_topic = {}
    for i, group in enumerate(groups[1]):
        print(f"Creating default Applications for Group: {i}/{len(groups[1])}\r", sep=' ', end='', flush=True)
        for j, topic in enumerate(random.sample(sose22_topics, random.randint(default_applications_per_student_range[0],
                                                                              default_applications_per_student_range[1]
                                                                              + 1))):
            TopicSelection.objects.create(group=group,
                                          topic=topic,
                                          priority=j + 1)
            if topic not in students_of_topic:
                students_of_topic[topic] = []
            students_of_topic[topic].extend(group.students.all())

    print("Creating default Applications for Group: Done!                      ")

    for group_size in range(2, default_max_group_size + 1):
        for i, group in enumerate(groups[group_size]):
            print(f"Creating special Applications for Group: {i}/{len(groups[group_size])}; Step {group_size - 2}/"
                  f"{default_max_group_size - 1}\r", sep=' ', end='', flush=True)
            for j, topic in enumerate(random.sample(sose22_special_topics[group_size],
                                                    min(len(sose22_special_topics[group_size]),
                                                        random.randint(default_applications_per_group_range[0],
                                                                       default_applications_per_group_range[1]
                                                                       + 1)))):
                if topic not in students_of_topic:
                    students_of_topic[topic] = []

                if any(student in group.students.all() for student in students_of_topic[topic]):
                    break

                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1)

                students_of_topic[topic].extend(group.students.all())

    print("Creating special Applications for Group: Done!                      ")

    # --- TERM WISE22/23 --- #

    wise22_term_registration_start = make_aware(datetime(2022, 11, 1, 0, 0, 0))
    wise22_term_registration_deadline = make_aware(datetime(2022, 11, 31, 23, 59, 59))
    print("Creating Term WiSe22")
    wise22 = Term.objects.create(name="WiSe22",
                                 registration_start=wise22_term_registration_start,
                                 registration_deadline=wise22_term_registration_deadline,
                                 active_term=True)
    wise22_topics = []
    wise22_special_topics = {}
    for j in range(default_course_per_term):
        print(f"Creating Courses: {j}/{default_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Course WiSe22 {j}",
                                            type=course_types[j % len(course_types)],
                                            term=wise22,
                                            registration_start=wise22_term_registration_start,
                                            registration_deadline=wise22_term_registration_deadline,
                                            description=f"Description of Course WiSe22 {j}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[j % len(faculties)],
                                            organizer=f"Organizer of Course WiSe22 {j}",
                                            )
        for j in range(default_topic_per_course):
            wise22_topics.append(Topic.objects.create(course=temp_course,
                                                      title=f"Topic {j} Course WiSe22 {j}",
                                                      max_slots=1,
                                                      min_slot_size=1,
                                                      max_slot_size=1,
                                                      description=f"Description of Topic {j} Course WiSe22 {j}"
                                                      ))
    print("Creating Courses: Done!                      ")

    for j in range(default_special_course_per_term):
        print(f"Creating special Courses: {j}/{default_special_course_per_term}\r", sep=' ', end='', flush=True)
        temp_course = Course.objects.create(title=f"Special Course WiSe22 {j}",
                                            type=course_types[j % len(course_types)],
                                            term=sose22,
                                            registration_start=sose22_term_registration_start,
                                            registration_deadline=sose22_term_registration_deadline,
                                            description=f"Description of Special Course WiSe22{j}",
                                            cp=random.randint(default_cp_range[0], default_cp_range[1]),
                                            faculty=faculties[j % len(faculties)],
                                            organizer=f"Organizer of Special Course WiSe22 {j}",
                                            )

        for j in range(default_topic_per_special_course):
            temp_max_slot_size = random.randint(1, default_max_group_size)
            temp_min_slot_size = random.randint(1, temp_max_slot_size)

            temp_topic = Topic.objects.create(course=temp_course,
                                              title=f"Topic {j} Special Course WiSe22 {j}",
                                              max_slots=j + 1,
                                              min_slot_size=temp_min_slot_size,
                                              max_slot_size=temp_max_slot_size,
                                              description=f"Description of Topic {j} Special Course WiSe22 {j}"
                                              )
            wise22_topics.append(temp_topic)
            for k in range(2, temp_max_slot_size + 1):
                if k not in wise22_special_topics:
                    wise22_special_topics[k] = []
                wise22_special_topics[k].append(temp_topic)
    print("Creating special Courses: Done!                      ")

    # --- APPLICATIONS TERM WISE22 --- #

    # TODO multiple collections
    students_of_topic = {}
    for i, group in enumerate(groups[1]):
        print(f"Creating default Applications for Group: {i}/{len(groups[1])}\r", sep=' ', end='', flush=True)
        for j, topic in enumerate(random.sample(wise22_topics, random.randint(default_applications_per_student_range[0],
                                                                              default_applications_per_student_range[1]
                                                                              + 1))):
            TopicSelection.objects.create(group=group,
                                          topic=topic,
                                          priority=j + 1)
            if topic not in students_of_topic:
                students_of_topic[topic] = []
            students_of_topic[topic].extend(group.students.all())

    print("Creating default Applications for Group: Done!                      ")

    for group_size in range(2, default_max_group_size + 1):
        for i, group in enumerate(groups[group_size]):
            print(f"Creating special Applications for Group: {i}/{len(groups[group_size])}; Step {group_size - 2}/"
                  f"{default_max_group_size - 1}\r", sep=' ', end='', flush=True)
            for j, topic in enumerate(random.sample(wise22_special_topics[group_size],
                                                    min(len(wise22_special_topics[group_size]),
                                                        random.randint(default_applications_per_group_range[0],
                                                                       default_applications_per_group_range[1]
                                                                       + 1)))):
                if topic not in students_of_topic:
                    students_of_topic[topic] = []

                if any(student in group.students.all() for student in students_of_topic[topic]):
                    break

                TopicSelection.objects.create(group=group,
                                              topic=topic,
                                              priority=j + 1)

                students_of_topic[topic].extend(group.students.all())

    print("Creating special Applications for Group: Done!                      ")

    print("\nFinished Creating DB!")
