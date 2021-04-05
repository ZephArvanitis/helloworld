# helloworld
*You* get a notification! And *you* get a notification!

Related to github (dot) com/twentyinc (slash) push_notifications_project. (That should be enough to prevent this coming up in searches)

[Live demo](https://apps.wxyzeph.com/helloworld/) (EDIT: this demo is running on a poor overburdened web server at the moment. It seems to be consistently up-ish, but thanks to what I believe is the interface between django and mysql, sometimes, there's 5-6 seconds of latency before django gets to process any request. Please note that I do not suggest that any website with five second latency is usable. I'm working on it.)


## Thoughts
This was a great deal of fun to think about and play with! In general, I feel I struggle far more with getting everything set up than with modifying it once it exists, and that held true here for sure. Much of my time was spent spinning up a new django app, planning out the UI, and generally getting all the pieces to play nicely with one another. If I were to do it again...well, I'll save that for the next section.

## Oops
In ding number one against Zeph on this challenge, I misread the prompt and thought you explicitly wanted the front and backend to talk to one another, so I dedicated far more time to that than was needed, which means I spent less time on fun edge cases and fine tuning the backend. Sorry about that! If you're willing to give me another hour, I'd be happy to show off my backend chops and just improve the *extremely* naive current implementation of `send_notifications`.

## Time
In total, my best estimate is that I spent 4.5-ish hours on this, not counting some necessary debugging on my server that I needed to get around to anyway (some middleware was getting greedy and causing very slow responses). An approximate breakdown:

 1. The first hour was spent getting a django app up and running locally and piecing together a semi-acceptable UI with a sample `fetch` request for connecting front and back ends.
 2. The second hour set up the backend database, fed data from there to the frontend, and visualized it in a list.
 3. The third hour I translated the ruby implementation you provided into python, implemented my naive `send_notifications`, and wrestled with cross-site scripting tokens. In the interests of time, I ditched the csrf token, since I couldn't figure out what part of the request construction wasn't working well. This is NOT a good idea for production use.
 4. The fourth and 4.5th hours I spent on frontend changes – adding the search bar to filter users, the toggle switches, and finally playing with the button behavior to give feedback on the push notification submissions.
 
 
## Running this
If you'd like to run this locally, you can! 

1. Plug this into an existing django app by cloning the repository at the same directory level as an existing `manage.py`. (For example, you could follow the installation instructions [here](https://www.djangoproject.com/start/), then the "Writing your first Django app" tutorial up till you create your first app. At that point, just clone this repository there instead of invoking `python manage.py startapp polls`.)

2. Add `helloworld` into `settings.py`:
```
INSTALLED_APPS = [
    ...
    'helloworld.apps.HelloWorldConfig',
]
```

3. Add it into `urls.py`:
```
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('helloworld/', include('helloworld.urls')),
]
```

4. Inside the newly cloned `helloworld` directory, run `npm install` and then `npm run build:dev` to build the tailwind css file and compile the typescript. (Note: the dev version of tailwindcss is very large - run `npm run tailwind:prod` to minify based on what's present in the html templates.)
5. Apply migrations via `python manage.py makemigrations`, then `python manage.py migrate`. By default, this will use a local sqlite database, which ought to be plenty for playing with the app.
6. Back in the root django site directory, run `python manage.py runserver`, and visit `http://127.0.0.1:8000/helloworld` in your favorite browser. 
7. To get the database set up, you'll want to create a django superuser and log in at `http://127.0.0.1:8000/admin`, then manually add "desktop" and "mobile" as device types. Once that's done, use any way you like of sending a GET request to the `http://127.0.0.1:8000/helloworld/random_number`. Each call will add one random user (name generated from common names lists), and each user has a chance of having zero, one, or two devices. Do that a few times until you have an acceptable-to-you number of users, then refresh the homepage and you'll be able to search for and select users to notify.


## What I'd do next
Given more time on this project, there are a few things I'd do:

 1. Fix glaring problems
     - The fact that I ignore the nonexistence of a CSRF token is a big security issue.
     - There's no testing at the moment, which there really should be! I'd add at least cursory tests over in `tests.py`.
     - Validate form input to ensure we don't send push notifications with empty notification strings.
     - Fix the fact that a GET request changes things in the database...a useful hack for getting stuff set up, but definitely not something to keep.
 2. Improve `send_notifications`. It's quite naive at the moment. First things to do:
     - Start logging what notifications we've sent and the outstanding notifications, so that if there's a restart, we can pick up where we left off.
     - Allow devices to opt out of notifications temporarily or permanently. Privacy and the sanctity of attention are big deals for me, so an opt-out here is high-priority in an open-ended problem like this.
     - Add rate limiting.
 3. Make other quality of life improvements
     - Introduce pagination on the user view list.
     - Improve tests further, catch some edge cases.
     - Add `__repr__` for database tables so the autogenerated admin pages are easier to understand.
     - Add some additional admin pages to support creating new users and viewing sent messages.
 4. Create infrastructure for...you know, whatever we're sending push notifications about. :D
