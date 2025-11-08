import os
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from . import views
from .models import ShopifySite

def shop_login_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.GET.get("id_token") is not None: # add in authentication later
            return fn(request, *args, **kwargs)
        if os.getenv("SHOPIFY_TOKEN") is not None:
            return fn(request, *args, **kwargs)
        elif not hasattr(request, 'session') or 'shopify' not in request.session:
            if "shop" in request.GET:
                return views.authenticate(request)
            else:    
                request.session['return_to'] = request.get_full_path()
                return redirect(reverse(views.login))
        elif "shop" in request.GET and request.GET["shop"]!=request.session["shopify"]["shop_url"]:
            request.session['return_to'] = request.get_full_path()
            return views.authenticate(request)
        
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def admin_embedded(fn):
    def wrapper(request, *args, **kwargs):
        if request.GET.get("id_token") is not None: # add in authentication later
            return fn(request, *args, **kwargs)
        request.session['return_to'] = request.get_full_path()
        return views.authenticate(request)
        
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
