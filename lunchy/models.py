from django.db import models

# creating a token each time you create a new user
# from http://cheng.logdown.com/posts/2015/10/27/how-to-use-django-rest-frameworks-token-based-authentication
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Create your models here.
class Person(models.Model):
    nickname = models.CharField(max_length=200, unique=True)
    bio = models.CharField(max_length=1000, null=True, blank=True)
    email = models.EmailField(default='user@domain.com')
    # facebook id
    fbid = models.BigIntegerField(null=True)
    # the current session
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __unicode__(self):
        return self.nickname

class Availability(models.Model):
    lunch_date = models.DateField(max_length=200)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.person.nickname + " " + str(self.lunchdate)

class Appointment(models.Model):
    lunch_date = models.DateField(max_length=200)
    persons = models.ManyToManyField(Person)
    place = models.CharField(max_length=1000, null=True)
    detail = models.CharField(max_length=1000, null=True)
    google_id = models.CharField(max_length=1000, null=True)

    def __unicode__(self):
        return self.lunch_date

    def get_persons(self):
        return ";".join([p.nickname for p in self.persons.all()])
    get_persons.short_description = "Persons Names"

class Shortcut(models.Model):
    # define which bot quick replies should lead to a specific story (by forcing a variable to True)
    bot_message = models.CharField(max_length=1000, unique=True)
    variable_name = models.CharField(max_length=40)
