
# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework.parsers import JSONParser

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


@api_view(['POST'])
def chat_message(request):
    logger.debug("chat_message was called")
    logger.debug("This is the request data: " + str(request.POST))
    assert request.POST['token'] == SLACK_TOKEN
    # don't reply to yourself
    user_name = request.POST['user_name']
    if not user_name == BOT_NAME:
        logger.debug("not the same user_name")
        # json_message = 'You said {}'.format(request.POST['text'])
        # add session with user_name and test "And Brussels"
        result = wit_chat(user_name, request.POST['text'] , {})
        logger.debug("Wit answered: " + str(result))
        return Response({"text": result["msg"],
            "result": result})