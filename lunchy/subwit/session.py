# import models
from lunchy.models import Person

# Session module
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

def close_session(request):
    # delete session opened by user to start a fresh clean conversation with the bot
    logger.debug("** Start closing session... **")
    # get the info from the bot
    context = request['context']
    entities = request['entities']

    # get the user session_key
    person = Person.objects.get(nickname = context["user_name"])
    logger.debug("Person found: " + context["user_name"])
    session_key = person.session_key
    # get session and delete it
    s = SessionStore(session_key = session_key)
    s.flush()
    logger.debug("Session should be cleaned up now")
    # clean up context too
    context = {}
    context["flushOk"] = True
    return context