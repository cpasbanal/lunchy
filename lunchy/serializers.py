from django.contrib.auth.models import User, Group
from lunchy.models import Availability, Person, Appointment
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')



class PersonSerializer(serializers.ModelSerializer):
    """
    Serializing all the Availabilities
    """

    class Meta:
        model = Person
        fields = ('id', 'bio', 'nickname', 'email')


class AvailSerializer(serializers.ModelSerializer):
    """
    Serializing all the Availabilities
    """
    person_nickname = serializers.CharField(source='person.nickname', read_only=True)

    class Meta:
        model = Availability
        fields = ('id', 'lunch_date', 'person_nickname')


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializing all the Appointments
    """

    class Meta:
        model = Appointment
        fields = ('id', 'lunch_date', 'place', 'detail')
