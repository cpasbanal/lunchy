# facebook bot functions to send structured messages
# stolen from https://github.com/davidchua/pymessenger/

import json

import requests
from requests_toolbelt import MultipartEncoder

DEFAULT_API_VERSION = "2.7"
PAGE_ACCESS_TOKEN = "EAAHpT0Gk1YMBAB3ECOo4HtHdlVGkeWrg3gs8cspqQqKLa1xZAO4ZA54rZBwby5eAF24Js3VNAigeuZAOZB6RHPvnCDOMBbPbI4I90PtlQk0d9pulCZC3F8N0UFgy6CNtIxXgPK3XcUy38LUdihRJbUlogUkPyc6o2XsRBs7Uo0TQZDZD"


class Bot():

    def __init__(self, *args, **kwargs):
        self.graph_url = 'https://graph.facebook.com/v{0}'.format(DEFAULT_API_VERSION)

    def send_text_message(self, recipient_id, message):
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': message
            }
        }
        return self._send_payload(payload)

    def send_message(self, recipient_id, message):
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': message
        }
        return self._send_payload(payload)

    def send_generic_message(self, recipient_id, elements):
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": elements
                    }
                }
            }
        }
        return self._send_payload(payload)

    def send_button_message(self, recipient_id, text, buttons):
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        return self._send_payload(payload)

    def send_quick_replies(self, recipient_id, text, replies):
        quick_replies = []
        for reply in replies:
            quick_replies.append({
                "content_type":"text",
                "title":reply["title"],
                "payload":reply.get("payload","DEFAULT_PAYLOAD")
            })
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "text": text,
                "quick_replies":quick_replies
            }
        }
        return self._send_payload(payload)

    def send_image(self, recipient_id, image_path):
        '''
            This sends an image to the specified recipient.
            Image must be PNG or JPEG.
            Input:
              recipient_id: recipient id to send to
              image_path: path to image to be sent
            Output:
              Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {}
                    }
                }
            ),
            'filedata': (image_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json()

    def send_image_url(self, recipient_id, image_url):
        ''' Sends an image to specified recipient using URL.
            Image must be PNG or JPEG.
            Input:
              recipient_id: recipient id to send to
              image_url: url of image to be sent
            Output:
              Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {
                            'url': image_url
                        }
                    }
                }
            )
        }
        return self._send_payload(payload)

    def _send_payload(self, payload):
        request_endpoint = '{0}/me/messages?access_token={1}'.format(self.graph_url, PAGE_ACCESS_TOKEN)
        response = requests.post(
            request_endpoint,
            json=payload
        )
        result = response.json()
        return result



