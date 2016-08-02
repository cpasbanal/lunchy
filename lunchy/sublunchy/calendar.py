''' Module used to set up the connecion with Google Calendar API
    thanks to: http://stackoverflow.com/questions/37754999/google-calendar-integration-with-django

'''

import os
import httplib2
import socks
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

service_account_email = 'lunchy@abstract-botany-137623.iam.gserviceaccount.com'
CLIENT_SECRET_FILE = os.getcwd() + '/randomlunch/lunchy/sublunchy/creds.p12'
SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]

def build_service(MAX_ATTEMPTS = 3):
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email=service_account_email,
        filename=CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    # pythonanywhere uses a proxy for free users (or else you have a [Errno101] Network is unreachable error) so use ProxyInfo
    try:
        # try to catch error 101 network error
        http = credentials.authorize(httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 'proxy.server', 3128)))
    except IOError:
        # an IOError exception occurred (socket.error is a subclass)
        # now we had the error code 101, network unreachable
        if MAX_ATTEMPTS <= 0:
            raise
        else:
            MAX_ATTEMPTS = MAX_ATTEMPTS - 1
            build_service(MAX_ATTEMPTS)

    service = build('calendar', 'v3', http=http)
    return service


def test_calendar(request):
    from datetime import datetime, date, time, timedelta
    import pytz
    from rest_framework.response import Response

    CALENDAR_ID = 'qi18u504r80oik5dmhhas4h4fs@group.calendar.google.com'
    # call calendar API
    service = build_service()
    # set the lunch to start at 12:15
    start_datetime = datetime.now()
    # localize the datetime according because Google Calendar needs it
    # according to http://stackoverflow.com/questions/18541051/datetime-and-timezone-conversion-with-pytz-mind-blowing-behaviour
    start_datetime = pytz.timezone('Europe/Paris').localize(start_datetime)
    # attendees = [{'email':'*********@gmail.com'}]
    # call the Google Calendar API
    event = service.events().insert(calendarId=CALENDAR_ID,
        sendNotifications=True,
        body={
            'summary': "A direct test",
            'description': 'A random lunch',
            'attendees' : [{'email':'jcroyere@gmail.com'}],
            'start': {'dateTime': start_datetime.isoformat()},
            'end': {'dateTime': (start_datetime + timedelta(hours=1, minutes=30)).isoformat()},
            'reminders': {
                'useDefault': False,
                'overrides': [
                  {'method': 'email', 'minutes': 24 * 60},
                  {'method': 'popup', 'minutes': 10},
                ],
            }
        }).execute()


    # event = service.events().get(calendarId=CALENDAR_ID, eventId=lunch.google_id).execute()
    # event['attendees'] = emails
    # updated_event = service.events().update(calendarId=CALENDAR_ID, sendNotifications=True, eventId=lunch.google_id, body=event).execute()
    return Response({
        "status"  : "done"
        })
