#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

import json

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# api.ai client token
CLIENT_ACCESS_TOKEN = 'c68495a1989d45a99ba34e9aca313569'

# this function will call api.ai with the text given in parameter (from Slack, Messenger...)
def apiai_chat(session_id, text, context):
    logger.debug("Calling api.ai chat function")
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()
    request.lang = 'fr'  # optional, default value equal 'en'
    request.session_id = session_id

    request.query = text

    response = request.getresponse()

    # response = requests.get(...)
    # data = response.json()
    logger.debug("Got response from api.ai")
    result = json.loads(response.read().decode('utf-8'))
    logger.debug(result)
    return result


