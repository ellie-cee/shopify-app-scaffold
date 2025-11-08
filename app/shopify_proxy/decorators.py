import os
import traceback
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from shopify_sites.models import ShopifySite
from django.shortcuts import render,redirect
import logging

logger = logging.Logger(__name__)

def validProxy(fn):
    def wrapper(request, *args, **kwargs):
        details =  {
            "shopDomain":request.GET.get("shop"),
            "customerId":request.GET.get("logged_in_customer_id"),
            "signature":request.GET.get("signature")
        }
        if os.environ.get("ISLOCAL")=="yes":
            return fn(request, *args, **kwargs)
        
        contentType = "text/html" if details.get("signature") is None else "application/liquid"
        if details is None or details.get("shopDomain") is None:
            return render(
                request,
                "proxy_fail.html",
                content_type=contentType
            )
        try:
            
            if not ShopifySite.validateSignature(request):
                return render(
                   request,
                    "proxy_fail.html",
                    content_type=contentType
                )
        except:
            traceback.print_exc()
            print("fayle")
            return render(
                   request,
                    "proxy_fail.html",
                    content_type=contentType
                )                             
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
