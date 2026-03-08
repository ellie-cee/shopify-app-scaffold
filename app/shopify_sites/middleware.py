import os
import traceback
from django.apps import apps
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse
import shopify

from esc.data import Data
from esc.graphql import ShopifyTokenGrantException
from .models import ShopifySite
import logging
logger = logging.Logger(__name__)
import shopify
import json
from django.core.cache import cache
import uuid

class ConfigurationError(BaseException):
    pass

class LoginProtection(object):
    def getSession(self,request:HttpRequest):
        sessionData = {}

        if request.headers.get("X-Shopify-Site") is not None:
            self.sessionType = "transient"
            self.sessionKey = request.headers.get("X-Shopify-Site")
            sessionData = {}
        elif request.GET.get("session") is not None:
                self.sessionType = "cacheSession"
                self.sessionKey = request.GET.get("session")
                sessionData = json.loads(cache.get(self.sessionKey,"{}"))
        elif request.POST.get("sessionKey") is not None:
                self.sessionType = "cacheSession"
                self.sessionKey = request.POST.get("sessionKey")
                sessionData = json.loads(cache.get(self.sessionKey,"{}"))
        else:
            self.sessionType = "djangoSession"
            self.sessionKey = request.session.get("sessionKey",uuid.uuid4())
            sessionData = dict(request.session)
        sessionData["sessionKey"] = self.sessionKey
        return sessionData

    def saveSession(self,request:HttpRequest,sessionData={}):
        if self.sessionType == "cacheSession":
            cache.set(self.sessionKey,json.dumps(sessionData))
        elif self.sessionType=="transient":
            return
        request.session["sessionKey"] = self.sessionKey

    def __init__(self, get_response):
        self.sessionType = None
        self.sessionKey = None
        self.get_response = get_response
        self.api_key = apps.get_app_config('shopify_sites').SHOPIFY_API_KEY
        self.api_secret = apps.get_app_config('shopify_sites').SHOPIFY_API_SECRET
        if not self.api_key or not self.api_secret:
            if not os.getenv("SHOPIFY_KEY"):
                raise ConfigurationError("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set in ShopifyAppConfig")
            else:
                self.api_key = os.getenv("SHOPIFY_KEY")
                self.api_secret = os.getenv("SHOPIFY_SECRET")
                
            #raise ConfigurationError("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set in ShopifyAppConfig")
        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)

    def __call__(self, request:HttpRequest):
        print(f"PATH: {request.path}")
        session = self.getSession(request)
        api_version = apps.get_app_config('shopify_sites').SHOPIFY_API_VERSION
        print(session.get("shopify"))
        if session.get("shopify") is None or session.get("shopify").get("authenticated") is None:
            if os.getenv("LOCALDEV_DOMAIN"):
                try:
                    shopifySite = ShopifySite.objects.filter(shopDomain=os.getenv("LOCALDEV_DOMAIN")).first()

                    session["shopify"] = {
                        "shop_url":shopifySite.shopDomain,
                        "shopId":shopifySite.id,
                        "access_token":shopifySite.token(),
                        "authenticated":True

                    }
                
                except:
                    traceback.print_exc()
                    print("Dewqdewqd")
                    pass
                print("poop")
            elif self.sessionType == "transient":
                try:
                    site = ShopifySite.objects.get(shopHost=self.sessionKey)
                    session["shopify"] = {
                        "shop_url":f"{site.shopDomain}",
                        "shopId":site.id,
                        "access_token":site.token(),
                         "authenticated":True
                    }
                except:
                    pass
                
            elif request.GET.get("shop") is not None and request.GET.get("embedded") is not None:
                print("embedded")
                site = ShopifySite.objects.filter(shopDomain=request.GET.get("shop")).first()
                print("SHITE IS",site)
                if site is None:
                    print("SITE IS NONE")
                    return redirect("/shopify")
                
                session["shopify"] = {
                    "shop_url":f"{site.shopDomain}",
                    "shopId":site.id,
                    "access_token":None,
                }
                
                
        
        if session.get("shopify") is not None:
            
            session["shopify"]["shop_url"] = session["shopify"]["shop_url"].split("/")[0]
            shop_url = f"{session['shopify']['shop_url']}/admin"
            shopify_session = shopify.Session(shop_url, api_version)
            shopify_session.token = session['shopify']['access_token']
            shopify.ShopifyResource.activate_session(shopify_session)

        self.saveSession(request,session)
        for key,value in session.items():
            request.session[key] = value
        

        response = self.get_response(request)
        shopify.ShopifyResource.clear_session()
        return response
class ShopifyEmbed:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = f"frame-ancestors https://{os.environ.get('SHOPIFY_DOMAIN')} https://admin.shopify.com;"
        return response
class ShopifyTokens:
    def __init__(self, get_response):
        self.get_response = get_response
    def process_exception(self,request:HttpRequest,exception):
        if isinstance(exception,ShopifyTokenGrantException) or isinstance(exception,ShopifyTokenException):
            if "json" in request.content_type:
                return HttpResponse(
                    json.dumps(Data.jsonify({
                        "message":f"Unable to retrieve session token for {exception.shopName}",
                        "status":401
                    })),
                    content_type="application/json",
                    status=401
                )
            else:
                return render(
                    request,
                    "token_error.html",
                    {
                        "shopName":exception.shopName,
                    }
                )

        return None
    def __call__(self, request:HttpRequest):
        response = self.get_response(request)
        return response