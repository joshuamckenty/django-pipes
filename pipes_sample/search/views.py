from pipes_sample.search.models import GoogleSearch, TwitterSearch
from django.shortcuts import render_to_response

def index(request):
    q = request.GET.get('q','Paris Hilton')
    results = GoogleSearch.fetch(q)
    ignored = TwitterSearch.fetch(q)
    return render_to_response("search.html", {'results':results,'q':q})

def twitter(request):
    q = request.GET.get('q','Barrack Obama')
    results = TwitterSearch.fetch(q)
    return render_to_response("twitter.html", {'results':results,'q':q})
