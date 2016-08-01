# module to query Open Weather Maps to answer "What's the weather?"
# TODO - add cache to OWM
# TODO - add id mapping with common cities

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

def get_forecast(request):
    # action received from user with context and entities
    # print('Received from user...', request['text'])
    context = request['context']
    entities = request['entities']

    # clean up context from previous forecast
    if context.get('forecast') is not None:
        del context['forecast']

    # Merge entities in context
    loc = first_entity_value(entities, 'location')
    if loc:
        context["location"] = loc
        request.session['weather_location'] = loc

    user_date = first_entity_value(entities, 'datetime')
    logger.debug("This is the datetime: " + str(user_date))
    if user_date:
        context["datetime"] = user_date
        request.session['weather_datetime'] = user_date

    logger.debug("This is request: " + str(request))

    # If location and date, then return weather
    if not "location" in context: # no location given
        logger.debug("No location given and context: " + str(context))
        context['missingLocation'] = True
    elif not "datetime" in context: # no date given
        logger.debug("No date given and context: " + str(context))
        context['missingDatetime'] = True
    else:
        logger.debug("Everything is ok and context: " + str(context))
        # context['forecast'] = 'cloudy'
        # using PyOWM API described at https://github.com/csparpa/pyowm/wiki/Usage-examples
        # get weather forceast for the next 5 days in the required location
        fc = owm.daily_forecast(context["location"], limit=5)
        # change when to noon to be more precise (probably asked for midnight otherwise)
        when = dateutil.parser.parse(context["datetime"])
        when.replace(hour=12)
        # get the weather for the specific date
        w = fc.get_weather_at(when)
        # get status for the wanted date (broken clouds, sunny...)
        status = w.get_detailed_status()

        # retrieve location to be explicit in the answer
        f = fc.get_forecast()
        owm_loc = f.get_location()
        precise_loc = "{}, {}".format(owm_loc.get_name(), owm_loc.get_country())

        logger.debug("This is the status: " + str(status) + " and loc: " + precise_loc + " at " + str(when))
        context['forecast'] = status
        context['weather_location'] = precise_loc

    return context

