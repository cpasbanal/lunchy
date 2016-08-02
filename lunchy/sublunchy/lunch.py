# import models
from lunchy.models import Availability, Appointment

# import specific submodules
from lunchy.sublunchy import calendar

# import some useful standard modules
from datetime import datetime, time
from datetime import timedelta
import pytz

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# Declare constant parameters
GUESTS_MIN = 4
CALENDAR_ID = 'qi18u504r80oik5dmhhas4h4fs@group.calendar.google.com'

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
            "status": "Lunch close",
            "info"  : "Not enough persons for " + str( lunch_date )
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
        "status"        : "Lunch open",
        "lunch_created" : lunch_created,
        "google_id"     : lunch.google_id,
        "attendees"     : emails,
        })