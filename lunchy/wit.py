from wit import Wit
# documentation and examples on the github page
# https://github.com/wit-ai/pywit

# import modules used by wit
# from lunchy.subwit.common import first_entity_value
from lunchy.subwit.forecast import get_forecast
from lunchy.subwit.lunchy import set_availability, update_email, cancel_availability
from lunchy.subwit.session import close_session

# import models
from lunchy.models import Person


# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# Session module
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

# my quickstart test
# access_token = "DSMDE3UL77ECC5X7TS2S75EZMANETCIE"
# old lunchy token
# access_token = "37BV5G3TT3MUDYU7Y27EBV2AEXJGETVL"
# new ai lunchy test
access_token = "QVPJ6U2NVQY6RFJ45XCUHQRSGLEOFB7I"

# initiate response
result = {"msg":[]}

def send(request, response):
    # print('Sending to user...', response['text'])
    logger.debug("Call send...")
    result["msg"].append({
        "text": response["text"].decode("utf-8"),
        "quickreplies": response.get("quickreplies", None)
        })
    logger.debug(result["msg"])

def handle_error(request):
    logger.debug("There was an error Wit returned action null, sorry")

# define all the actions wit can do
actions = {
    'send': send,
    'getForecast': get_forecast,
    'setAvailability': set_availability,
    'updateEmail': update_email,
    'cancelAvailability': cancel_availability,
    'closeSession': close_session,
    None: handle_error,
}

client = Wit(access_token=access_token, actions=actions)
client.logger.setLevel(logging.DEBUG)

def wit_chat(session_id, text, context):
    # Calling high-level API to get the end message we should return to the client

    # first, resume the previous session
    # get the user session_key
    person, person_created = Person.objects.get_or_create(nickname = context["user_name"])
    logger.debug("Person found: " + context["user_name"])
    session_key = person.session_key
    # logger.debug("Session key returned: " + str(session_key))
    # s = SessionStore(session_key = session_key)
    # if session previously existed, then resume it
    s = SessionStore()
    if session_key and s.exists(session_key):
        # logger.debug("this is my session_key: " + session_key)
        s = SessionStore(session_key = session_key)
    else:   # session doesn't exists so create one
        logger.debug("Session doesn't exist any more so create it")
        s.create()
        # update session_key of the person object (add user_name to ease log debug in Wit)
        person.session_key = context["user_name"] + "__" + str(s.session_key)
        person.save()
        session_key = s.session_key

    # get previous context and return empy dict if empty
    previous_context = s["context"] if "context" in s else {}
    logger.debug("The previous context is: " + str(previous_context))
    # update context with previous context
    context.update(previous_context)
    logger.debug("New context is: " + str(context))

    # session_id = 'my-user-session-42'
    logger.debug("** calling run_actions **")
    # reset result message
    result["msg"] = []
    context = client.run_actions(session_key, text, context, max_steps=8)
    logger.debug("** after calling run_actions **")
    logger.debug('The session state is now: ' + str(context))
    result["context"] = context

    # store context for this session
    s["context"] = result["context"]
    s.save()

    return result

# client.interactive()