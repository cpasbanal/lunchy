from wit import Wit

# import modules used by wit
# from lunchy.subwit.common import first_entity_value
from lunchy.subwit.forecast import get_forecast
from lunchy.subwit.lunchy import set_availability, update_email, cancel_availability
from lunchy.subwit.session import close_session

# documentation and examples on the github page
# https://github.com/wit-ai/pywit

# my quickstart test
access_token = "DSMDE3UL77ECC5X7TS2S75EZMANETCIE"
# lunchy token
access_token = "37BV5G3TT3MUDYU7Y27EBV2AEXJGETVL"


# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

# initiate response
result = {"msg":""}

def send(request, response):
    # print('Sending to user...', response['text'])
    result["msg"] = result["msg"] + response["text"].decode("utf-8") + "\n"
    logger.debug(result["msg"])
    # result["msg"] = response["text"]

# define all the actions wit can do
actions = {
    'send': send,
    'getForecast': get_forecast,
    'setAvailability': set_availability,
    'updateEmail': update_email,
    'cancelAvailability': cancel_availability,
    'closeSession': close_session,
}

client = Wit(access_token=access_token, actions=actions)
client.logger.setLevel(logging.DEBUG)

def wit_chat(session_id, text, context):
    # Calling high-level API to get the end message we should return to the client
    # session_id = 'my-user-session-42'

    logger.debug("** calling run_actions **")
    # reset result message
    result["msg"] = ""
    # logger.debug("Current session: " + str(session_id))
    context = client.run_actions(session_id, text, context, max_steps=8)
    logger.debug("** after calling run_actions **")
    logger.debug('The session state is now: ' + str(context))
    result["context"] = context
    return result

# client.interactive()