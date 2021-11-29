from django.db import models


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_type = models.CharField(max_length=200)
    register_from = models.DateTimeField('date registration opens')
    registration_deadline = models.DateTimeField('registration deadline')
    course_description = models.TextField('course description')
    max_participants = models.IntegerField('maximum number of participants', default=9999)
    cp = models.IntegerField('CP')
    # maybe use choices for category and field?
    category = models.CharField(max_length=200)
    faculty = models.CharField(max_length=200)
    # organizer or instructors?
    organizer = models.CharField(max_length=200)

    def __str__(self):
        return self.course_name


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course_<id>/<filename>
    return 'course_{0}/{1}'.format(instance.course.id, filename)


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=200)
    max_participants = models.IntegerField('maximum number of participants', default=999)
    topic_description = models.TextField('topic description')
    topic_file = models.FileField(upload_to='course_directory_path')

    def __str__(self):
        return self.topic_name


class Student(models.Model):
    tucan_id = models.CharField(max_length=200, primary_key=True)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.tucan_id



