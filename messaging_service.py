import itertools
import random
import string
import time

from .models import ApplicationUser, UserDevice
from .notifications import Messenger

class MessagingService(object):
    """Our very own messaging service! This does three things:

      * It holds on to a Messenger, to minimize overhead of setting up a new
        one each time we send messages (if this isn't allowed, then I'll move
        the Messenger instantiation into send_notifications, but keep
        unregistered token initialization as it is)
      * It keeps track of what tokens are not registered. This avoids unneeded
        database calls.
      * It orchestrates sending of notifications given user_ids and a
        notification body.
    """

    def __init__(self):
        """Set up the messenger we'll use.
        """
        self.messenger = Messenger()
        # Get initial unregistered tokens from the database
        bad_tokens_query = (UserDevice.objects
                                      .filter(token_not_registered=True)
                                      .values_list('device_token'))
        # Result of values_list looks like [(token1,), (token2,), ...]
        # Extract actual tokens.
        bad_tokens = [dtt[0] for dtt in bad_tokens_query]
        # De-duplicate, just in case
        self.not_registered_tokens = set(bad_tokens)

    def set_all_tokens_registered(self):
        """Re-register all tokens, or eventually you won't be able to send
        notifications at all.
        """
        UserDevice.objects.all().update(token_not_registered=False)

    def _get_all_tokens_for_users(self, user_ids):
        """Get device tokens for all users passed in.

        == Parameters:
        user_ids::
        A list of integer user ids to send to.
        """
        device_tokens_tuples = (UserDevice.objects
                                          .filter(user__id__in=user_ids)
                                          .select_related('applicationuser')
                                          .values_list('device_token'))
        # Result of values_list looks like [(token1,), (token2,), ...]
        # Extract actual tokens.
        # (meta-note: I refactor once I do something three times)
        device_tokens = [dtt[0] for dtt in device_tokens_tuples]

        # De-dupe the tokens list, just in case
        all_user_tokens = list(set(device_tokens))

        # Remove tokens that have previously returned as not registered
        tokens = [token for token in all_user_tokens
                  if token not in self.not_registered_tokens]
        return tokens

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
        tokens = self._get_all_tokens_for_users(user_ids)
        
        # Short circuit if we're not notifying anyone
        if len(tokens) == 0:
            return {"status_code": 200, "devices_notified": 0}

        # Chunk it into batches of <500 and send 'em off.
        chunk_size = 490
        chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)] 

        max_total_tries = len(chunks) * 2
        total_tries = 0
        total_devices_notified = 0
        had_any_success = False

        while chunks and total_tries < max_total_tries:
            chunk = chunks[0]
            total_tries += 1
            # Send it off
            response = self.messenger.send(chunk, notification_body)
            # check how it went
            status_code = response["status_code"]
            if status_code == 200:
                # Went great!
                # Housekeeping to note that we succeeded and remove bad tokens
                had_any_success = True
                bad_tokens = response["not_registered_tokens"]
                (UserDevice.objects
                           .filter(device_token__in=bad_tokens)
                           .update(token_not_registered=True))
                self.not_registered_tokens = self.not_registered_tokens.union(
                    bad_tokens)
                # No need to send notifications to this chunk anymore
                chunks = chunks[1:]
                # Increment our total notified count
                not_notified_count = len(bad_tokens)
                total_devices_notified += len(chunk) - not_notified_count
            elif status_code == 500:
                # Error, no messages sent. Try again after we've done the other chunks
                chunks = chunks[1:] + [chunk]
            else:
                # Either we messed up and sent more than 500 tokens or some other error happened.
                # Still try again.
                chunks = chunks[1:] + [chunk]

        if not had_any_success:
            # Uh oh, in spite of our attempts we weren't able to notify anyone...
            return {"status_code": 500}

        return {"status_code": 200, "devices_notified": total_devices_notified}