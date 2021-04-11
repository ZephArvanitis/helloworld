import itertools
import random
import string
import time

from .models import ApplicationUser, UserDevice


class Messenger(object):

    def __init__(self):
        """You must call this before trying to send messages.
        Heavy network initialization, so it takes a while.
        """
        # We do some heavy network initialization
        time.sleep(5)
        self._not_registered_tokens = set()

    def send(self, tokens, notification_body):
        """
        Sends the notification body to the devices with the specified tokens
    
        == Parameters:
        tokens::
        A list of tokens to send to. Must be 500 or fewer.
        notification_body::
        A string representing the body of the notification. eg. "Hello world!"
    
        == Returns:
        A dictionary containing a status code and possibly a list of tokens that are no longer valid
        If :status_code is 500, there was an error and no messages were sent.
        If :status_code is 400, there was a request error
        If :status_code is 200, the hash will also contain :not_registered_tokens
        Tokens in :not_registered_tokens are no longer valid and those devices will not receive notifications
        You should *not* repeatedly try to send messages to tokens that are no longer registered or you may be banned
        """
        if random.random() < 0.02:
            return {"status_code": 500}
        
        if len(tokens) > 500:
            return {"status_code": 400}

        time.sleep(1)  # network stuff

        not_registered_tokens = [token for token in tokens
                                if token in self._not_registered_tokens or
                                random.random() < 0.05]
        self._not_registered_tokens = self._not_registered_tokens.union(not_registered_tokens)

        return {"status_code": 200, "not_registered_tokens": not_registered_tokens}

    @staticmethod
    def generate_token():
        """Generates a device token

        Ordinarily this would come from the device itself, but a simple version is provided here for your convenience
        """
        return "".join([random.choice(string.ascii_uppercase) for _ in range(8)])