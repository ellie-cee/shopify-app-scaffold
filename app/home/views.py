import os
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from site_auth.decorators import requiresLogin
from django.http import HttpResponse
from shopify_sites.models import ShopifySite
import json
import logging
from django.conf import settings
from django.template import RequestContext
from django.core.mail import EmailMultiAlternatives
from .lmno import EmailStatus, jsonify,sendEmail
from appointment.models import Appointment,StaffMember,AppointmentRequest
from django.views.decorators.csrf import csrf_exempt
from xyz import settings
from shopify_sites.decorators import shop_login_required
from .models import ApplicationVariant,ResumeVariant
import docx
from docx.text.hyperlink import Hyperlink
from django.http import FileResponse
import datetime
import random
logger = logging.Logger(__name__)
import pathlib
import pymupdf


# Create your views here.




def dashboard(request):
    
    print(request.session.get("dewqdewq"))
    return render(
        request,
        "shopify/index.html",
        {}
    )
def homePage(request):
    print(request.headers)
    if request.GET.get("embedded") is not None and request.GET.get("id_token") is not None:
        return render(
            request,
            "shopify/index.html",
            {}
        )
    else:
        return render(
            request,
            "index.html",
            {}
        )
def logJson(payload):
    logger.error(
        json.dumps(payload,indent=1)
    )
def jsonResponse(payload,status=200):
    payload["status"] = status
    return HttpResponse(
        json.dumps(payload),
        content_type="application/json",
        status=status
    )
def getJsonPayload(request):
    return json.loads(request.body.decode("utf-8"))

def install(request):
    shopifySite,created = ShopifySite.objects.get_or_create(shopDomain=request.session["shopify"].get("shop_url"))
    if created:
        shopifySite.accessToken = request.session["shopify"].get("access_token")
        details = shopifySite.shopDetails()
    return redirect("/shopify/home")

def testFake(request):
    
    
    pass
def testEmail(request):
    
    result:EmailStatus = sendEmail(
        recipient="cassadyeleanor@gmail.com",
        subject="hey now",
        context={"message":"butts lol"},
        sender="ellie@elliecee.xyz",
        templatePrefix="2fa"
    )
    print(result)
    return render(
        request,
        "test.html",
        {"message":result.message}
    )
    
    
@csrf_exempt
@shop_login_required
def showTagForm(request):
    return render(
        request,
        "shopify/resume_form.html",
        {
            "variants":ResumeVariant.objects.all()
        }
    )


@csrf_exempt

def tagResume(request):
    
    applicationVariant,created = ApplicationVariant.objects.get_or_create(name=request.POST.get("name"))
    if created:
        applicationVariant.purged = False
        applicationVariant.fileName = ""
        applicationVariant.details = request.POST.get("details")
        
    taggedPdfPath,fileName = applicationVariant.process(request.POST.get("variant"))
    return FileResponse(
        open(taggedPdfPath, 'rb'),
        as_attachment=True,
        filename=fileName
    )
    
    
    
    
    
    

@csrf_exempt
def viewed(request):
    
    payload = getJsonPayload(request)
    print(dict(request.session))
    
    sourceId = payload.get("inquirer")
    details = None
    context = {
        "sourceId":sourceId,
        "location":payload.get("link"),
        "lead":"None detected"   
    }
    if sourceId is not None:
        try:
            details = ApplicationVariant.objects.get(identifier=sourceId)
            context["lead"] = details.name
        except:
            pass
    
    result:EmailStatus = sendEmail(
        recipient="cassadyeleanor@gmail.com",
        subject=f"Site View from {context.get("lead")}",
        context=context,
        sender="ellie@elliecee.xyz",
        templatePrefix="siteClick"
    )
    
    return jsonResponse(
        {"recieved":"true"},
        200
    )
    
                                                                                    

