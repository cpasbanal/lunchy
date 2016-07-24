# lunchy app URL Configuration
from django.conf.urls import url
from lunchy import views, slack #,calendar


# Availability API
#   http://blog.mwaysolutions.com/2014/06/05/10-best-practices-for-better-restful-api/
#   GET  /availabilities?nickname={nickname}&date=yyyy-mm-dd
#   Test url http://jcroyere.pythonanywhere.com/lunchy/availabilities?nickname=jo&date=2016-07-10
#   POST /availabilities/{user nickname}/{yyyy}/{mm}/{dd}
#   Test url http://jcroyere.pythonanywhere.com/lunchy/availabilities/jo/2016/07/10

# sample token for jeremie
# HTTP Headers
# Authorization Token 4c39ba1941d806d9cc4baba1a9c6feeecb587bdc


urlpatterns = [
    url(r'^api/v1/availabilities/$', views.avail_api),
    url(r'^api/v1/availabilities/(?P<avail_id>\d+)$', views.avail_api),

    url(r'^api/v1/persons/$', views.person_api),
    url(r'^api/v1/persons/(?P<person_id>\d+)$', views.person_api),

    # url(r'^api/v1/calendar/$', calendar.test_calendar),

    url(r'^api/v1/message/$', slack.chat_message),

    # url(r'^availabilities/$', views.avail_api),
    # url(r'^availabilities$', views.availability_api),
    # url(r'^availabilities\/(?P<nickname>\w{0,50})\/(?P<year>\d{4})\/(?P<month>\d{2})\/(?P<day>\d{2})$', views.avail_api),
]