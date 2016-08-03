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
# impor FB Bot calls
from lunchy.sublunchy.bot import Bot

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

    # get the JSON POSTed
    data = request.data
    logger.debug(data)
    # create the FB bot that will send messages
    bot = Bot()

    for entry in data["entry"]:
        for message in entry["messaging"]:
        # Check to make sure the received call is a message call
        # This might be delivery, optin, postback for other events
            if 'message' in message:
                # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                # are sent as attachments and must be handled accordingly.
                logger.debug(message["message"]["text"])
                # Retrieve user info from facebook API
                fbid = message['sender']['id']
                user_info = get_facebook_user_info(fbid = fbid)
                # add mock session_id because will be treated in wit_chat, pass user_name in context
                result = wit_chat("session_id", message['message']['text'] , {"user_name":user_info["user_name"]})
                logger.debug("Wit answered: " + str(result))
                # use the facebook API to post a message to the user
                for msg in result["msg"]:
                    logger.debug("This is msg: " + str(msg))
                    # reponse depends on if wit sends quickreplies
                    if msg.get("quickreplies", None):
                        # quickreplies must be less than or equal to 20 characters
                        # if 2 or less quickreplies, send quick reply, else, send button
                        if len(msg["quickreplies"]) <= 2:
                            # send a quick reply cause short enough
                            replies = [{"title": reply} for reply in msg["quickreplies"]]
                            logger.debug("Replies: " + str(replies))
                            status = bot.send_quick_replies(fbid, msg["text"], replies)
                        else:   # send a button message
                            buttons = [{"type":"postback",
                                        "title":reply,
                                        "payload":"LUNCHY_NO_PAYLOAD"}
                                        for reply in msg["quickreplies"]
                                    ]
                            status = bot.send_button_message(fbid, msg["text"], buttons)
                    else:   # simply send the plain message
                        status = bot.send_text_message(fbid, msg["text"])
                logger.debug(status)
    return Response("ok done")

def get_facebook_user_info(fbid):
    # retrieve facebook info wether from facebook id
    # first, check if this id is already in database
    try:
        person = Person.objects.get(fbid = fbid)
        user_name = person.nickname
    except Person.DoesNotExist:
        logger.debug("Facebook id isn't already in database")
        # so call the facbook API to get user info
        # https://developers.facebook.com/docs/graph-api/reference/user/
        user_details_url = "https://graph.facebook.com/v2.7/{}".format(fbid)
        user_details_params = {'fields':'first_name,last_name', 'access_token':PAGE_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        logger.debug(user_details)
        user_name = "{0} {1}".format(user_details['first_name'], user_details['last_name'])
        ## currently removed the email part because I need the permissions to read the user email ##
        # # check if user already exists with current email, else create the entry with user_name = first name + last name
        # try:
        #     person = Person.objects.get(email = user_details["email"])
        # except Person.DoesNotExist:
        person, person_created = Person.objects.get_or_create(nickname = user_name)
            # # update the user email in the database
            # if not person.email:
            #     person.email = user_details['email']
        # and store the data into our database
        person.fbid = fbid
        person.save()
    return dict({"user_name": user_name})