import logging

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe

from pendle.utils import current_year


log = logging.getLogger(__name__)
UID = __name__

def user_label(user, template="%(name)s (%(username)s)", allow_tags=False):
    label = template % {'name': user.get_full_name(),
                        'first': user.first_name,
                        'last': user.last_name,
                        'username': user.username}
    if allow_tags:
        label = mark_safe(label)
    return label

User.__unicode__ = user_label
User._meta.ordering = ('last_name', 'first_name')

class Profile(models.Model):
    YEAR_CHOICES = ((1, "1: Freshman"),
                    (2, "2: Sophomore"),
                    (3, "3: Junior"),
                    (4, "4: Senior"),
                    (5, "5: BFA"))
    user = models.ForeignKey(User, unique=True)
    id_number = models.CharField("ID number", max_length=16, null=True,
        blank=True, help_text="Number on the user's ID card.")
    phone_number = models.CharField(max_length=24, null=True, blank=True)
    address = models.TextField(blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True,
                                            choices=YEAR_CHOICES)
    graduation_date = models.DateField(null=True, blank=True)
    staff_notes = models.TextField(blank=True)
    picture = models.ImageField(upload_to='pictures/profiles', null=True,
                                blank=True)
    signed_agreement = models.BooleanField(default=False,
        help_text="User has signed the equipment agreement form.")


    def __unicode__(self):
        return u"%s's Profile" % (self.user.get_full_name() or self.user)


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True,
                            help_text="The title of the department.")
    subject_code = models.CharField(max_length=4, blank=True)
    users = models.ManyToManyField(User, related_name='departments',
                                   blank=True,
                                   help_text="People in this department.")

    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
 

class Course(models.Model):
    subject_code = models.CharField(max_length=6,
                                    help_text="For example: TIM")
    number = models.CharField(max_length=8, help_text="For example: 201.01")
    title = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = [('subject_code', 'number')]
        ordering = ['subject_code', 'number']

    def __unicode__(self):
        return u"%s%s" % (self.subject_code, self.number)


class ScheduledCourse(models.Model):
    SEMESTER_CHOICES = (('FA', "Fall"),
                        ('SP', "Spring"),
                        ('SU', "Summer"))
    course = models.ForeignKey(Course, related_name='semesters')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    year = models.PositiveSmallIntegerField(default=current_year)
    instructor = models.ForeignKey(User, null=True, blank=True,
                                   related_name='instructed_courses')
    students = models.ManyToManyField(User, related_name='courses')

    class Meta:
        unique_together = [('course', 'semester', 'year')]
        ordering = ['-year', 'semester', 'course']

    def __unicode__(self):
        return u"%s, %s %s" % (self.course, self.get_semester_display(),
                               self.year)


class Training(models.Model):
    name = models.CharField(max_length=75, unique=True)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name='training',
                                   through='TrainingCertificate')
    
    class Meta:
        verbose_name_plural = "training"
    
    def __unicode__(self):
        return self.name


class TrainingCertificate(models.Model):
    user = models.ForeignKey(User)
    training = models.ForeignKey(Training)
    date_completed = models.DateField(null=True, blank=True)


def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)

def find_user(query):
    try:
        user = User.objects.get(username=query)
    except User.DoesNotExist:
        user = User.objects.get(profile__id_number=query)
    return user

signals.post_save.connect(create_profile, sender=User, dispatch_uid=UID)

