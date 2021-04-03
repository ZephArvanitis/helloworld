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
        self.not_registered_tokens = set()

    def send_notifications(self, user_ids, notification_body):
        """
        Sends the notification to the users with the given ids

        == Parameters:
        user_ids::
        A list of integer user ids to send to.
        notification_body::
        A string representing the body of the notification. eg. "Hello world!"
    
        == Returns:
        A dictionary containing a status code and the number of devices to which the notification was sent
        If :status_code is 500, there was an error and no messages were sent
        If :status_code is 400, there was a request error
        If :status_code is 200, the dictionary will also contain the devices-notified count
        """
        # Let's go with the naivest possible implementation to start
        # (I'm worried about time)

        # Notify all devices for all users, except ones that are no longer registered.
        users = ApplicationUser.objects.filter(id__in=user_ids)
        tokens_by_user = [[device.device_token for device in user.devices
                           if device.device_token not in self.not_registered_tokens]
                          for user in users]
        # Flatten and de-dupe the tokens list, just in case
        tokens = list(set(itertools.chain(*tokens_by_user)))

        # Short circuit if we're not notifying anyone
        if len(tokens) == 0:
            return {"status_code": 200, "devices_notified": 0}

        print("tokens:", tokens)
        # Chunk it into batches of <500 and send 'em off.
        chunk_size = 490
        chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)] 

        max_total_tries = len(chunks) * 2
        total_tries = 0
        total_devices_notified = 0

        while chunks and total_tries < max_total_tries:
            chunk = chunks[0]
            total_tries += 1
            # Send it off
            response = self.send(chunk, notification_body)
            # check how it went
            status_code = response["status_code"]
            if status_code == 200:
                # Went great! Remove chunk and increment total_devices_notified
                chunks = chunks[1:]
                not_notified_count = len(response["not_registered_tokens"])
                print(len(chunk), not_notified_count)
                total_devices_notified += len(chunk) - not_notified_count
            elif status_code == 500:
                # Error, no messages sent. Try again after we've done the other chunks
                chunks = chunks[1:] + [chunk]
            else:
                # Either we messed up and sent more than 500 tokens or some other error happened.
                print("Unknown error in Messenger.send_notifications")
                chunks = chunks[1:] + [chunk]

        print("Notified {x} devices".format(x=total_devices_notified))
        if total_devices_notified == 0:
            # Uh oh, in spite of our attempts we weren't able to notify anyone...
            return {"status_code": 500}

        return {"status_code": 200, "devices_notified": total_devices_notified}


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
                                if token in self.not_registered_tokens or
                                random.random() < 0.05]
        self.not_registered_tokens = self.not_registered_tokens.union(not_registered_tokens)

        return {"status_code": 200, "not_registered_tokens": not_registered_tokens}

    @staticmethod
    def generate_token():
        """Generates a device token

        Ordinarily this would come from the device itself, but a simple version is provided here for your convenience
        """
        return "".join([random.choice(string.ascii_uppercase) for _ in range(8)])