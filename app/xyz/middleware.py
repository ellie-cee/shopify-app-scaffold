import os
from django.apps import apps
from django.urls import reverse

class CorsHeaders(object):
    def __init__(self, get_response):
        self.get_response = get_response
        pass
    def __call__(self, request):    
        response = self.get_response(request)
        response["Access-Control-Allow-Credentials"] = "true"
        return response