#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

# import subfunctions
from lunchy.subapiai.forecast import get_forecast
from lunchy.subwit.lunchy import set_availability, update_email, cancel_availability
# from lunchy.subwit.session import close_session

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")


# define all the actions wit can do
actions = {
    'getForecast': get_forecast,
    'setAvailability': set_availability,
    'updateEmail': update_email,
    'cancelAvailability': cancel_availability,
}

# webhook called by api.ai for some intents
# sample app at https://github.com/api-ai/apiai-weather-webhook-sample/
@api_view(['POST'])
def webhook(request):
    logger.debug("Webhook called")
    # recover the POST parameters
    data = request.data
    # logger.debug(data)
    result = data.get('result', None)
    # logger.debug(result)
    if result is None:
        return Response({})
    parameters = result.get("parameters")

    # get the function we should call
    action = result.get("action")
    speech = actions[action](parameters)
    logger.debug("Speech to user: " + str(speech))

    return Response({
                "speech": speech,
                "displayText": speech,
                "data": {},
                "contextOut": [],
                "source": "OWM",
            })