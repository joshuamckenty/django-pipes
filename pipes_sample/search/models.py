from django.db import models
import django_pipes as pipes

# Create your models here.
class GoogleSearch(pipes.Pipe):
    uri = "http://ajax.googleapis.com/ajax/services/search/web"

    @staticmethod
    def fetch(q):
        resp = GoogleSearch.objects.get({'v':1.0, 'q':q})
        if resp and hasattr(resp, "responseData") and hasattr(resp.responseData, "results"):
            return resp.responseData.results

class TwitterSearch(pipes.Pipe):
    uri = "http://search.twitter.com/search.json"
    
    @staticmethod
    def fetch(q):
        resp = TwitterSearch.objects.get({'q':q})
        if resp and hasattr(resp, "results"):
            return resp.results
