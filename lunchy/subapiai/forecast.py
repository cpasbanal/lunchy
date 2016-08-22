# module to query Open Weather Maps to answer "What's the weather?"
# TODO - add cache to OWM
# TODO - add id mapping with common cities
# TODO - add temperature in °C

import dateutil.parser

# using PyOWM to access Open Weather Map
# https://github.com/csparpa/pyowm
import pyowm

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

def get_forecast(parameters):
    logger.debug("** Get forecast called **")

    # Merge entities in context (location and date)
    loc = parameters.get("geo-city", None)
    if loc is None or len(loc) == 0:
        logger.debug("No location given")
        return "Dans quelle ville et quel pays ?"
    user_date = parameters.get("date", None)
    logger.debug("Parameters: " + str(parameters))
    logger.debug("User_date:" + str(user_date))
    # logger.debug(user_date)
    # logger.debug(user_date.get("rfcString", None))
    if user_date is None or len(user_date) == 0:
        logger.debug("No date given")
        return

    # If location and date, then return weather
    # using PyOWM API described at https://github.com/csparpa/pyowm/wiki/Usage-examples
    # get weather forceast for the next 5 days in the required location
    fc = owm.daily_forecast(loc, limit=5)
    # change when to noon to be more precise (probably asked for midnight otherwise)
    try:
        when = dateutil.parser.parse(user_date)
    except:
        when = dateutil.parser.parse(user_date.get("rfcString", None))
    logger.debug("When: " + str(when))
    when.replace(hour=12, minute=0)
    # get the weather for the specific date
    try:
        w = fc.get_weather_at(when)
    except pyowm.exceptions.not_found_error.NotFoundError:
        logger.debug("Date not in range")
        return "Pouvez-vous redonner une date d'ici 5 jours max ?"
        # context["outOfRange"] = True
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
        # context['forecast'] = status
        # context['weather_location'] = precise_loc
        # context['temp_morning'] = round(temp['morn'])
        # context['temp_evening'] = round(temp['eve'])
        forecast = dict({
                "forecast": status,
                "weather_location": precise_loc,
                "temp_morning": round(temp['morn']),
                "temp_evening": round(temp['eve'])
            })
        res = "Le temps prévu à {weather_location} est : {forecast}. Il fera environ {temp_morning} °C le matin et {temp_evening} °C l'après-midi.".format(**forecast)
        return res
    return "Désolé, nous avons rencontré un petit problème..."

