# module to receive message from Facebook Messenger and do whatever needed
# inspirated from https://abhaykashyap.com/blog/post/tutorial-how-build-facebook-messenger-bot-using-django-ngrok

# import Rest framework modules
from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import requests

# import models
from lunchy.models import Person

# import wit calls
from lunchy.wit import wit_chat

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# Session module
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

PAGE_ACCESS_TOKEN = "EAAHpT0Gk1YMBAB3ECOo4HtHdlVGkeWrg3gs8cspqQqKLa1xZAO4ZA54rZBwby5eAF24Js3VNAigeuZAOZB6RHPvnCDOMBbPbI4I90PtlQk0d9pulCZC3F8N0UFgy6CNtIxXgPK3XcUy38LUdihRJbUlogUkPyc6o2XsRBs7Uo0TQZDZD"
VALIDATION_TOKEN = "thisisjustatokentoverify"

@api_view(['POST', 'GET'])
def chat_message(request):
    logger.debug("** Messenger API was called **")
    # if request.GET['hub.verify_token'] == VALIDATION_TOKEN:
    #     challenge = int(request.GET['hub.challenge'])
    #     logger.debug(challenge)
    #     return Response(challenge)
    # else:
    #     return Response('Error, invalid token')
    data = request.data
    logger.debug(data)
    for entry in data["entry"]:
        for message in entry["messaging"]:
        # Check to make sure the received call is a message call
        # This might be delivery, optin, postback for other events
            if 'message' in message:
                # Print the message to the terminal
                logger.debug(message["message"]["text"])
                # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                # are sent as attachments and must be handled accordingly.
                post_facebook_message(message['sender']['id'], message['message']['text'])
    return Response("ok done")

def post_facebook_message(fbid, received_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":received_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    logger.debug(status.json())