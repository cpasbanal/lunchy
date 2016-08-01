
# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework.parsers import JSONParser

# import models
from lunchy.models import Person

# import wit calls
from lunchy.wit import wit_chat


# slack bot tutorial
# https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
# can't work on Pythonanywhere because socket are filtered for free users
# https://www.pythonanywhere.com/forums/topic/2185/

SLACK_BOT_TOKEN = "xoxb-62604641204-0b23Q7Asvz9W7z2SXFqe0lq5"
SLACK_TOKEN = "jiGg6v1HO1wTaJHsKQJ00w40"
BOT_NAME = 'slackbot'

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# Session module
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

@api_view(['POST'])
def chat_message(request):
    logger.debug("** Chat_message was called **")
    logger.debug("This is the request data: " + str(request.POST))
    assert request.POST['token'] == SLACK_TOKEN
    # don't reply to yourself
    user_name = request.POST['user_name']
    if not user_name == BOT_NAME:
        logger.debug("A real user is calling (not the bot)")
        # get the user session_key
        person, person_created = Person.objects.get_or_create(nickname = user_name)
        logger.debug("Person found: " + user_name)
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
            # update session_key of the person object
            person.session_key = s.session_key
            person.save()
            session_key = s.session_key

        # json_message = 'You said {}'.format(request.POST['text'])
        # get previous context and return empy dict if empty
        previous_context = s["context"] if "context" in s else {}
        # add the user_name to the context
        previous_context["user_name"] = user_name
        logger.debug("The previous context is: " + str(previous_context))
        # add session with session_key (and user_name to ease debug in wit) and previous context
        result = wit_chat(user_name + "__" + str(session_key), request.POST['text'] , previous_context)
        logger.debug("Wit answered: " + str(result))
        # store context for this session
        s["context"] = result["context"]
        s.save()
        return Response({"text": result["msg"], "result": result})