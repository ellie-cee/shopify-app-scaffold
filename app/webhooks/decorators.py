import os
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from . import views
from .models import ShopifySite

def valid_webhook(fn):
    def wrapper(request, *args, **kwargs):
        if request.session.get("webhook") is None:
            return HttpResponse(
                content="Access Denied",
                content_type="text/plain",
                status=401
            )
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
