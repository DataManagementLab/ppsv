from backend.models import Assignment,possible_assignments
from course.models import Group,TopicSelection, Topic

def get_all_collections_as_list():
    collections = {}
    for application in TopicSelection.objects.all():
        if application.group in collections:
            if application.collection_number in collections[application.topic]:
                collections[application.group][application.collection_number].append(application)
            else :
                collections[application.group][application.collection_number] = [application]
        else:
            collections[application.group] = {}
            collections[application.group][application.collection_number] = [application]
    return collections


all_collections = get_all_collections_as_list()

all_projects = Topic.objects.all()
distance = 2
chance_of_mutation = 10
max_chance_of_mutation = 80
increased_mutation_cycle = 300
max_number_of_iterations = 100000
population_size = 3

def main():
    # generate extended preference list
    pass



