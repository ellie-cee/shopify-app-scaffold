import traceback
from django.shortcuts import render
from django.template import RequestContext
from .decorators import validProxy
from home.views import getJsonPayload,jsonResponse
from home.lmno import sendEmail
from logging import Logger
import os
from django.views.decorators.csrf import csrf_exempt

logger = Logger(__name__)

# Create your views here.
def responseContentType(request):
    proxied = request.GET.get("shop") is not None and request.GET.get("signature") is not None
    return "application/liquid" if proxied else "text/html"
    

def index(request):
    return render(
        request,
        "proxy.html",
        content_type=responseContentType()
    )
    
@validProxy
def test(request):
    return render(
        request,
        "proxy/test.html",
        content_type=responseContentType(request)
    )

def getProxyDetails(request):
    rc = RequestContext(request)
    rc.get('proxyDetails')

@validProxy
def contactForm(request):
    return render(
        request,
        "contact.html",
        content_type=responseContentType(request)
    )
    
@csrf_exempt
def sendContact(request):
    payload = getJsonPayload(request)
    
    try:
        message = sendEmail(
            recipient="cassadyeleanor@gmail.com",
            subject=f"New Inquiry from {payload.get('name')}",
            context=payload,
            templatePrefix="contact-notification",
            replyTo=payload.get("email"),
        )
    except:
        logger.error(traceback.format_exc())
        return jsonResponse(
            {
                "message":"error!"
            },
        
            204
        )
    return jsonResponse(
        {
            "message":"hooray",
        },
        200
    )