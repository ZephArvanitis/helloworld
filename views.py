from django.shortcuts import render
from django.http import JsonResponse


# Homepage
def index_view(request):
    """Render the index page for this app.
    """
    template_name = 'helloworld/index.html'
    kwargs = {"title": "Push Notification Central"}
    return render(request, template_name, kwargs)


def get_random_number(request):
    if request.method == "GET":
    # if request.method == "GET" and request.is_ajax():
        # https://xkcd.com/221/
        random_number = 4  # chosen by fair dice roll. Guaranteed random.
        return JsonResponse({"success": True,
                             "random_number": random_number}, status=200)
    return JsonResponse({"success": False}, status=400)
