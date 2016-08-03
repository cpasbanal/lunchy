
# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework.parsers import JSONParser

# # import models
# from lunchy.models import Person

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
        logger.debug("A real user is calling from Slack (not the bot)")
        # add mock session_id because will be treated in wit_chat, pass user_name in context
        result = wit_chat("session_id", request.POST['text'] , {"user_name":user_name})
        logger.debug("Wit answered: " + str(result))
        return Response({"text": result["msg"], "result": result})
    return Response({})