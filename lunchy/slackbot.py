

import os
from slackclient import SlackClient

# slack bot tutorial https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

SLACK_BOT_TOKEN = "xoxb-62604641204-0b23Q7Asvz9W7z2SXFqe0lq5"
BOT_NAME = 'lunchybot'

# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# slack_client = SlackClient(SLACK_BOT_TOKEN)
slack_client = SlackClient("xoxb-62604641204-0b23Q7Asvz9W7z2SXFqe0lq5")


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)