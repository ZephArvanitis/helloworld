from django.shortcuts import render
from django.http import JsonResponse

import random
import string

from .models import ApplicationUser, DeviceType, UserDevice


# Homepage
def index_view(request):
    """Render the index page for this app.
    """
    template_name = 'helloworld/index.html'
    users = ApplicationUser.objects.all()
    kwargs = {"title": "Push Notification Central",
              "users": users
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
        device = UserDevice.objects.create(user=user, device_type=device_type)


def post_add_random_users(request):
    if request.method == "POST":
        for _ in range(10):
            _add_random_user()

        return JsonResponse({"success":True}, status=200)
    return JsonResponse({"success":False}, status=400)


def get_random_number(request):
    if request.method == "GET":
        # https://xkcd.com/221/
        random_number = 4  # chosen by fair dice roll. Guaranteed random.
        return JsonResponse({"success": True,
                             "random_number": random_number,
                             }, status=200)
    return JsonResponse({"success": False}, status=400)
