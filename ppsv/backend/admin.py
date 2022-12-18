from django.contrib import admin
from .models import Assignment
from import_export import resources
from course.models import TopicSelection
from import_export.fields import Field

# Register your models here.

admin.site.register(Assignment)


class TopicSelectionResource(resources.ModelResource):
    """TopicSelectionResource

    This model represents the resource of TopicSelection for an export. It states the colum names as well as the
    representation of how a single datum in a colum will be represented.

    :attr TopicSelectionResource.id: the id of the TopicSelection
    :type TopicSelectionResource.id: int
    :attr TopicSelectionResource.topic_representation: the topicID of the topic of TopicSelection followed by the topics name in parenthesis
    :type TopicSelectionResource.topic_representation: string
    :attr TopicSelectionResource.course_representation: the courseID of the course of the topic of TopicSelection followed by the courses name in parenthesis
    :type TopicSelectionResource.course_representation: string
    :attr TopicSelectionResource.group_representation: the groupID of the group of TopicSelection followed by the groups name in parenthesis
    :type TopicSelectionResource.group_representation: string
    :attr TopicSelectionResource.collection_number: the collection number of the TopicSelection
    :type TopicSelectionResource.collection_number: int
    :attr TopicSelectionResource.priority: the priority of the TopicSelection
    :type TopicSelectionResource.priority: int
    """

    id = Field(attribute='id', column_name='ApplicationID')
    topic_representation = Field(column_name='TopicID(topic name)')
    course_representation = Field(column_name='CourseID(course name)')
    group_representation = Field(column_name='GroupID(size)')
    collection_number = Field(attribute='collection_number', column_name='collection number')
    priority = Field(attribute='priority', column_name='priority')

    class Meta:
        """
        Defines the model this resource is based on as TopicSelection. Excludes fields that shall not be shown when
        exported and states an export order of the fields.
        """

        model = TopicSelection
        exclude = ('group', 'topic', 'motivation')
        export_order = ('id', 'topic_representation', 'course_representation', 'group_representation', 'collection_number', 'priority')

    def dehydrate_topic_representation(self, application):
        """topic representation
        :param application: the application attribute

        :return: the representation of a topic
        :rtype: string
        """
        application_topic = getattr(application.topic, "id", "unknown")
        application_topic_title = getattr(application.topic, "title", "unknown")
        return '%d(%s)' % (application_topic, application_topic_title)

    def dehydrate_course_representation(self, application):
        """course representation
        :param application: the application attribute

        :return: the representation of a course
        :rtype: string
        """
        application_course = getattr(application.topic.course, "id", "unknown")
        application_course_title = getattr(application.topic.course, "title", "unknown")
        return '%d(%s)' % (application_course, application_course_title)

    def dehydrate_group_representation(self, application):
        """group representation
        :param application: the application attribute

        :return: the representation of a group
        :rtype: string
        """
        application_group = getattr(application.group, "id", "unknown")
        application_group_size = getattr(application.group, "size", "unknown")
        return '%d(%d)' % (application_group, application_group_size)
