# import models
from lunchy.models import Person, Availability, Appointment

# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
# import serializers
from lunchy.serializers import AvailSerializer, PersonSerializer, AppointmentSerializer

# import some useful standard modules
from datetime import datetime, time
from datetime import timedelta
import pytz

# import specific modules
from lunchy import calendar

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# Declare constant parameters
GUESTS_MIN = 4
CALENDAR_ID = 'qi18u504r80oik5dmhhas4h4fs@group.calendar.google.com'
#CALENDAR_ID = 'servicesfactory.sncf@gmail.com'

############# Availability API ################
@api_view(['GET', 'POST', 'DELETE'])
def avail_api(request, avail_id=None):
    # API can create, get or delete an availability for a person (== a user)
    # add new availability (and create Person if doesn't exist)
    if request.method == 'POST':
        # recover the POST parameters
        nickname = request.POST['nickname']
        avail_date = datetime.strptime(request.POST['avail_date'], "%Y-%m-%d")
        # query the database to see if user already exists (or create it)
        person, person_created = Person.objects.get_or_create(nickname = nickname)
        # add email if given
        if "email" in request.POST:
            from django.db import IntegrityError
            try:
                # update email of the person object
                person.email = request.POST["email"]
                person.save()
                email_updated = True
            except IntegrityError:
                logger.info("Cannot update email %s, record already exists" % request.POST["email"])
                email_updated = False
        # query the database to create the new availability of the user
        availability, avail_created = Availability.objects.get_or_create(
            lunch_date = avail_date,
            person = person
        )
        # try to create a lunch if enough participants
        results = handle_lunch( avail_date )
        # TODO add to response if lunch was created

        return Response({
            "nickname"  : person.nickname,
            "email"     : person.email,
            "avail_id"  : availability.id,
            "avail_date": avail_date,
            "user_created": person_created,
            "email_updated": email_updated,
            "avail_created": avail_created,
            "lunch_results": results
            })
    # cancel availability
    elif request.method == 'DELETE':
        if avail_id:
            try:
                avail = Availability.objects.get(id=avail_id)
                # and delete the availability
                avail_result = avail.delete()
                # consider removing a lunch if no longer enough participants
                lunch_result = handle_lunch( avail.lunch_date )
            except Availability.DoesNotExist:
                avail_result = "Availability already deleted"
                lunch_result = None
        return Response({
            "id": avail_id,
            "avail_result":avail_result,
            "lunch_result":lunch_result
            })
    # get the availability for a custom date or a nickname
    else: # request.method == 'GET':
        # prepare the query (querysets are lazy) - or request all if no parameters passed
        avails = Availability.objects.all()
        # recover the nickname from GET parameters
        nickname = request.GET.get('nickname')
        if nickname is not None:
            # filter the availabilities on the nickname
            avails = avails.filter(person__nickname = nickname)
        # recover the availability date from GET parameters
        avail_date = request.GET.get('date')
        if avail_date is not None:
            avail_date = datetime.strptime(avail_date, "%Y-%m-%d")
            avails = avails.filter(lunch_date = avail_date)
        serializer = AvailSerializer(avails, many=True)
        return Response(serializer.data)

############# Person API ################
@api_view(['GET', 'POST', 'PUT'])
def person_api(request, person_id=None):
    # API can get, create or update user
    # action depends on the HTTP request
    # create a new user
    if request.method == "POST":
        # get data from the POST request
        data = JSONParser().parse(request)
        # user the serializer defined in serializer.py
        serializer = PersonSerializer(data=data)
        if serializer.is_valid():
            # update the model and database
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == 'PUT':
        logger.debug("Beginning of PUT section")
        # query the record on the database
        put = request.data
        person = Person.objects.get(nickname = put.get("nickname"))
        # create an instance of serializer for the current record
        serializer = PersonSerializer(person, data=request.data)
        # update the record
        if serializer.is_valid():
            # update the model and database
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    else: # request.method == 'GET':
        persons = Person.objects.all()
        # recover the person id from the url
        if person_id:
            persons = persons.filter(id = person_id)
        # recover the nickname from GET parameters
        nickname = request.GET.get('nickname')
        if nickname is not None:
            persons = persons.filter(nickname = nickname)
        # create a serializer with the database object to return the data in JSON
        serializer = PersonSerializer(persons, many=True)
        return Response(serializer.data)

############# Lunch functions ################
def handle_lunch(lunch_date):
    # create, update or delete lunches depending on the guest number
    # check for a custom date if enough users, then create the lunch
    logger.debug("Handling lunch for: " + str( lunch_date))
    # query the database and get related person objects
    avails = Availability.objects.select_related().filter(lunch_date = lunch_date)
    # logger.debug("The availabilities: " + str(avails))

    # get the lunch data
    lunches = Appointment.objects.filter( lunch_date = lunch_date )
    # check if a lunch already exists
    if len(lunches) > 0:    # lunch already created
        lunch_created = False
        # currently select the first result because only one Appointment per day
        # --> should be updated if want to handle several lunches each day
        lunch = lunches[0]
    else:
        lunch_created = True
    # call calendar API
    service = calendar.build_service()

    # check if enough persons are available for the requested lunch date
    if len(avails) < GUESTS_MIN:
        # not enough guests, delete the Appointment and remove the Google Calendar invitation
        logger.info("Not enough persons for " + str(lunch_date))
        # if lunch was already created, delete the Google event
        if not lunch_created:
            # delete Google event
            event = service.events().delete(calendarId=CALENDAR_ID, eventId=lunch.google_id).execute()
            # and delete the Appointment object
            lunch = Appointment.objects.get( id = lunch.id ).delete()
        return dict({
            "status": "ok",
            "info"  : "Not enough persons for " + str( lunch_date ),
            "google_event" : event
            })

    else:   # enough attendees so create or update lunch
        # create or update the lunch
        logger.debug("*** Creating or updating Appointment object ***")
        # get all the attendees emails
        # expected format >> attendees = [{'email':'*********@gmail.com'}]
        emails = [{'email':avail.person.email} for avail in avails]
        logger.debug("Attendees emails: " + str(emails))
        # if the lunch was created in the database, then create the Google Calendar event
        if lunch_created:
            # add the Appointment id to the lunch title
            lunch_title = "[Lunchy] Un déj aléatoire" #.format( lunch.id )
            # set the lunch to start at 12:15
            start_datetime = datetime.combine(lunch_date, time(12, 15))
            # start_datetime = datetime.now()
            # localize the datetime according because Google Calendar needs it
            # according to http://stackoverflow.com/questions/18541051/datetime-and-timezone-conversion-with-pytz-mind-blowing-behaviour
            start_datetime = pytz.timezone('Europe/Paris').localize(start_datetime)
            # call the Google Calendar API
            try:
                event = service.events().insert(calendarId=CALENDAR_ID,
                    sendNotifications=True,
                    body={
                        'summary': lunch_title,
                        'description': 'A random lunch',
                        'attendees' : emails,
                        'start': {'dateTime': start_datetime.isoformat()},
                        'end': {'dateTime': (start_datetime + timedelta(hours=1, minutes=30)).isoformat()},
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                              {'method': 'email', 'minutes': 24 * 60},
                              {'method': 'popup', 'minutes': 15},
                            ],
                        }
                    }).execute()
            except OSError:
                return dict({
                    "status":"Error",
                    "info" : "There was an issue contacting google, please try again later"
                    })
            # update the Appointment with google id to update or delete the event afterwards
            # create the lunch object in the Appointment Model
            lunch = Appointment.objects.create( lunch_date=lunch_date, google_id=event["id"] )
            # lunch.google_id = event["id"]
            # lunch.save()
        else: # update lunch
            # add new person email to the lunch
            # retrieve the event from the API.
            logger.debug("*** Updating the Appointment ***")
            event = service.events().get(calendarId=CALENDAR_ID, eventId=lunch.google_id).execute()
            event['attendees'] = emails
            updated_event = service.events().update(calendarId=CALENDAR_ID, sendNotifications=True, eventId=lunch.google_id, body=event).execute()

    # create a serializer with the database object to return the data in JSON
    #serializer = AppointmentSerializer(lunch, many=True)
    return dict({
        "status"        : "ok",
        "lunch_created" : lunch_created,
        "google_id"     : lunch.google_id,
        "attendees"     : emails,
        })

def index(request):
    # availabilities = Availability.objects.order_by("lunch_date")
    return "Just the index"