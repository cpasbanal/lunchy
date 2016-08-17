''' Create shortcuts in and out between user message and wit
        out : message from Wit to user --> add keys to quick replies
        in : use the keys to force a story in Wit
'''

# TODO store in database the mapping and make a web interface of this module

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")

class Shortcut():
    def __init__(self, *args, **kwargs):
        self.keys_out = {
                "Quelle est la météo ?" : "weather",
                "Un déj aléatoire ?"    : "randomlunch",
            }