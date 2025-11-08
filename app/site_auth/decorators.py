import os
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from shopify_sites.models import ShopifySite
from django.shortcuts import render,redirect
import logging

logger = logging.Logger(__name__)

def requiresLogin(fn):
    def wrapper(request, *args, **kwargs):
        userSession = request.session.get("userDetails")
        if userSession is None:
            return render(request,"login.html")
        userPermissions = userSession.get("permissions")
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
