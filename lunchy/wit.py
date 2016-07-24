from wit import Wit

# documentation and examples on the github page
# https://github.com/wit-ai/pywit

access_token = "DSMDE3UL77ECC5X7TS2S75EZMANETCIE"

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

def first_entity_value(entities, entity):
    # find the wanted entity from the wit request
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    # print('Sending to user...', response['text'])
    print(response['text'])

def get_forecast(request):
    # action received from user with context and entities
    # print('Received from user...', request['text'])
    context = request['context']
    entities = request['entities']

    loc = first_entity_value(entities, 'location')
    if loc:
        context['forecast'] = 'sunny'
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']

    return context


# define all the actions wit can do
actions = {
    'send': send,
    'getForecast': get_forecast,
}

client = Wit(access_token=access_token, actions=actions)

def wit_chat(session_id, context, text):
    # Calling high-level API to converse with the bot
    # session_id = 'my-user-session-42'
    # context0 = {}
    # context1 = client.run_actions(session_id, 'what is the weather in London?', context0)
    # print('The session state is now: ' + str(context1))
    # context2 = client.run_actions(session_id, 'and in Brussels?', context1)
    # print('The session state is now: ' + str(context2))
    new_context = client.run_actions(session_id, text, context)
    logger.debug("The session state is now: " + str(new_context))
    return new_context

if __name__ == "__main__":
    # call the interactive session
    session_id = 'my-user-session-42'
    context0 = {}
    context1 = wit_chat(session_id, "What is the weather in London?", context0)
    print('The session state is now: ' + str(context1))
    context2 = client.run_actions(session_id, 'and in Brussels?', context1)
    print('The session state is now: ' + str(context2))
    # client.interactive()