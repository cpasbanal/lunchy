# module to query Open Weather Maps to answer "What's the weather?"
# TODO - add cache to OWM
# TODO - add id mapping with common cities
# TODO - add temperature in °C

import dateutil.parser

# using PyOWM to access Open Weather Map
# https://github.com/csparpa/pyowm
import pyowm

# import wit specific module
from lunchy.subwit.common import first_entity_value

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

owm = pyowm.OWM('620667215b058dcedea98a7353174546', # You MUST provide a valid API key
                language='fr')  # change default answer to fr

# Session
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

def get_forecast(request):
    # action received from user with context and entities
    # print('Received from user...', request['text'])
    context = request['context']
    entities = request['entities']
    # session_id = request['session_id']

    # store all the context information in a specific namespace to avoid conflict
    if not "weather" in context:
        context["weather"] = {}
    # reset forced weather variable
    context.pop('forceWeather', None)

    logger.debug("** Get forecast called **")

    # Merge entities in context (location and date)
    loc = first_entity_value(entities, 'location')
    if loc:
        # logger.debug("location given")
        context["weather"]["location"] = loc
        context.pop('missingLocation', None)
    user_date = first_entity_value(entities, 'datetime')
    if user_date:
        # logger.debug("datetime given")
        context["weather"]["datetime"] = user_date
        context.pop('missingDatetime', None)

    # If location and date, then return weather
    if not "location" in context.get("weather", None): # no location given
        context['missingLocation'] = True
        logger.debug("No location given and context: " + str(context))
    elif not "datetime" in context.get("weather", None): # no date given
        context['missingDatetime'] = True
        logger.debug("No date given and context: " + str(context))
    else:
        logger.debug("Everything is ok and context: " + str(context))
        # using PyOWM API described at https://github.com/csparpa/pyowm/wiki/Usage-examples
        # get weather forceast for the next 5 days in the required location
        fc = owm.daily_forecast(context["weather"]["location"], limit=5)
        # change when to noon to be more precise (probably asked for midnight otherwise)
        when = dateutil.parser.parse(context["weather"]["datetime"])
        when.replace(hour=12)
        # get the weather for the specific date
        try:
            w = fc.get_weather_at(when)
        except pyowm.exceptions.not_found_error.NotFoundError:
            logger.debug("Date not in range")
            context["outOfRange"] = True
        else:
            # get status for the wanted date (broken clouds, sunny...)
            status = w.get_detailed_status()
            temp = w.get_temperature(unit='celsius')

            # retrieve location to be explicit in the answer
            f = fc.get_forecast()
            owm_loc = f.get_location()
            precise_loc = "{}, {}".format(owm_loc.get_name(), owm_loc.get_country())

            logger.debug("This is the status: " + str(status) + " and loc: " + precise_loc +
                " at " + str(when) + " and temp is: " + str(temp))
            context['forecast'] = status
            context['weather_location'] = precise_loc
            context['temp_morning'] = round(temp['morn'])
            context['temp_evening'] = round(temp['eve'])

            # we answered the client, so delete the previous weather context
            del context["weather"]
    return context

