from wit import Wit

# import modules used by wit
from lunchy.subwit.common import first_entity_value
from lunchy.subwit.forecast import get_forecast


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
    logger.debug(response['text'])
    # result["msg"] = result["msg"] + "\n" + str(response['text'])
    result["msg"] = response["text"]

def merge(request):
    context = request['context']
    entities = request['entities']

    logger.debug("** Merge was called with context: " + str(context) + " and entities: " + str(entities))

    # if 'location' in context:
    #     del context['location']
    # location = first_entity_value(entities, 'location')
    # if location:
    #     context['location'] = location

    # sentiment = first_entity_value(entities, 'sentiment')
    # if sentiment:
    #     context['ack'] = 'Glad you liked it.' if sentiment == 'positive' else 'Hmm.'
    # elif 'ack' in context:
    #     del context['ack']
    return context

# define all the actions wit can do
actions = {
    'send': send,
    'merge': merge,
    'getForecast': get_forecast,
}

client = Wit(access_token=access_token, actions=actions)
client.logger.setLevel(logging.DEBUG)

def wit_chat(session_id, text, context):
    # Calling high-level API to get the end message we should return to the client
    session_id = 'my-user-session-42'
    logger.debug("** calling run_actions **")
    context = client.run_actions(session_id, text, context)
    logger.debug("** after calling run_actions **")
    logger.debug('The session state is now: ' + str(context))
    result["context"] = context
    return result

client.interactive()