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

# api.ai client token
CLIENT_ACCESS_TOKEN = 'c68495a1989d45a99ba34e9aca313569'


def main():
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.lang = 'fr'  # optional, default value equal 'en'

    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"

    request.query = "Hello"

    response = request.getresponse()

    print (response.read())

if __name__ == '__main__':
    main()