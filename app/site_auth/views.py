from django.shortcuts import render,redirect

from .models import User,AuthRequest
from home.views import jsonResponse,getJsonPayload
from datetime import datetime
import logging

logger = logging.getLogger("auth")




# Create your views here.

def loginStatus(request):
    if request.session.get("userDetails") is not None:
        logger.error("logged in")
        return jsonResponse(
            {
                "url":"/"
            },
            status=302
        )
    if request.session.get("AUTHORIZATION_REQUEST") is not None:
        authRequest = AuthRequest.objects.get(id=request.session.get("AUTHORIZATION_REQUEST"))
        logger.error("in process")
        return jsonResponse(
            {
                "userEmail":authRequest.requestUser.censoredEmail()
            },
            status=200
        )
    return jsonResponse(
        {},
        status=404
    )
    


def login(request):
    if request.session.get("userDetails") is not None:
        return jsonResponse(
            {
                "url":"/"
            },
            status=302
        )
        return  redirect("/")
    """
    elif request.session.get("AUTHORIZATION_REQUEST") is not None:
       authRequest = AuthRequest.objects.get(id=request.session.get("AUTHORIZATION_REQUEST"))
      return jsonResponse(
         {
          "user"
            }
        )
        return render(
            request,
            "code.html",
            {
                "user":authRequest.requestUser
            }
        )
    """
    payload = getJsonPayload(request)
    userEmail = payload.get("email")
    user = User.objects.filter(email=userEmail).first()
    if user is None:
        return jsonResponse(
            {
                "message":"Invalid Email address"
            },
            status=404
        )
    auth = user.createAuth()
    request.session["AUTHORIZATION_REQUEST"] = str(auth.id)
    return jsonResponse(
        {
            "userEmail":user.censoredEmail()
        },
        status=200
    )
    
def getActiveRequest(request):
    priorRequestId = request.session["AUTHORIZATION_REQUEST"]
    if priorRequestId is not None:
        return AuthRequest.objects.get(id=priorRequestId)
    return None

def logout(request):
    request.session.clear()
    return redirect("/")

def validate(request):
    
    activeRequest = getActiveRequest(request)
    if activeRequest is None:
        return jsonResponse(
        {
            "message":"Completed",
            "url":"/"
        },
        302
    )
    payload = getJsonPayload(request)
    code = payload.get("authCode")
    logger.error(code)
    if not activeRequest.matches(code):
        return jsonResponse(
            {
                "message":"Invalid code"
            },
            404
        )
    if activeRequest.isExpired():
        return jsonResponse(
            {
                "message":"Code has expired"
            },
            404
        )
    activeUser = activeRequest.requestUser
    request.session["userDetails"] = {
        "name":activeUser.name,
        "id":str(activeUser.id),
        "email":activeUser.email,
        "permissions":[x.name for x in activeUser.permissions.all()]
    }
    
    try:
        del request.session["AUTHORIZATION_REQUEST"]
    except:
        pass
    
    for auth in AuthRequest.objects.filter(requestUser=activeUser):
        auth.delete()
    return jsonResponse(
        {
            "message":"Completed",
            "url":"/"
        },
        302
    )
    return redirect("/")
def restart(request):
    priorRequestId = request.session["AUTHORIZATION_REQUEST"]
    if priorRequestId is not None:
        request = AuthRequest.objects.get(priorRequestId)
        request.delete()
        del request.session["AUTHORIZATION_REQUEST"]
    return jsonResponse(
        {},
        status=302
    )
def resend(request):
    priorRequestId = request.session["AUTHORIZATION_REQUEST"]
    if priorRequestId is not None:
        authRequest = AuthRequest.objects.get(id=priorRequestId)
        requestUser = authRequest.requestUser
        newAuthRequest = requestUser.createAuth(authRequest=authRequest)
        return jsonResponse(
            {},
            status=200
        )
        return render(
            request,
            "code.html",
            {
                "user":authRequest.requestUser
            }
        )
    else:
        return jsonResponse(
            {},
            status=200
        )
        return login(request)
    pass
    