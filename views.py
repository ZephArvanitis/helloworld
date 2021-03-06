from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import random
import string

from .models import ApplicationUser, DeviceType, UserDevice
from .notifications import Messenger
from .messaging_service import MessagingService


messaging_service = MessagingService()


# Homepage
def index_view(request):
    """Render the index page for this app.
    """
    template_name = 'helloworld/index.html'
    # devices = UserDevice.objects.select_related('device_type').all()
    device_types = DeviceType.objects.all()
    device_type_dict = {device_type.id : device_type.type_name
                        for device_type in device_types}
    users = ApplicationUser.objects.prefetch_related('userdevice_set').all()
    # Format the information we need in the template
    users_for_display = [{"name": user.name,
                          "id": user.id,
                          "device_types": [device_type_dict[dev.device_type_id]
                                           for dev in user.userdevice_set.all()]}
                         for user in users]

    kwargs = {"title": "Push Notification Central",
              "users": users_for_display
             }
    return render(request, template_name, kwargs)


def _add_random_user():
    # top 10 male/female first names in California, 2008
    common_first_names = ["Daniel", "Anthony", "Angel", "Jacob", "David",
                          "Alexander", "Andrew", "Joshua", "Christopher",
                          "Jose", "Isabella", "Emily", "Sophia", "Samantha",
                          "Ashley", "Natalie", "Mia", "Emma", "Abigail", "Ava"]
    # top 20 last names in the US
    common_last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                         "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                         "Hernandez", "Lopez", "Gonzales", "Wilson", "Anderson",
                         "Thomas", "Taylor", "Moore", "Jackson", "Martin"] 
    # my conception of common email domains
    email_domains = ["gmail.com", "yahoo.com", "comcast.net"]

    first_name = random.choice(common_first_names)
    last_name = random.choice(common_last_names)
    email_domain = random.choice(email_domains)
    full_name = "{first} {last}".format(first=first_name, last=last_name)
    user_email = "{first}.{last}@{domain}".format(
        first=first_name, last=last_name, domain=email_domain)

    user = ApplicationUser.objects.create(name=full_name, email=user_email)

    # Between zero and two devices
    number_of_devices = random.choice(range(3))
    device_types = DeviceType.objects.all()
    devices = []
    for _ in range(number_of_devices):
        device_type = random.choice(device_types)
        device_token = Messenger.generate_token()
        device = UserDevice.objects.create(user=user, device_type=device_type,
                                           device_token=device_token)


def post_add_random_users(request):
    """Add ten random users and their devices
    """
    if request.method == "POST":
        for _ in range(10):
            _add_random_user()

        return JsonResponse({"success":True}, status=200)
    return JsonResponse({"success":False}, status=400)


@csrf_exempt  # TODO: Fix this!!  Time-saving shortcut as my csrf token is acting up.
def post_notify_users(request):
    """Notify the users indicated of something VERY important
    """
    if request.method == "POST":
        received_json_data = json.loads(request.body.decode("utf-8"))
        if not "user_ids" in received_json_data and "notification_body" in received_json_data:
            return JsonResponse({"success": False}, status=400) 
        user_ids = received_json_data["user_ids"]
        notification_body = received_json_data["notification_body"]

        notifications_status = messaging_service.send_notifications(user_ids, notification_body)

        status_code = notifications_status["status_code"]
        if status_code == 200:
            return JsonResponse({"success": True, "notified": notifications_status["devices_notified"]})
        return JsonResponse({"success": False}, status=status_code)
    return JsonResponse({"success": False}, status=400) 


def get_random_number(request):
    """That old sample ajax call, as a placeholder
    """
    if request.method == "GET":
        # https://xkcd.com/221/
        _add_random_user()
        random_number = 4  # chosen by fair dice roll. Guaranteed random.
        return JsonResponse({"success": True,
                             "random_number": random_number,
                             }, status=200)
    return JsonResponse({"success": False}, status=400)
