import os
from django.apps import apps
from django.urls import reverse
from django.http import HttpResponse
import shopify
import logging
import shopify
import json
from django.core.cache import cache
import uuid
from .models import ShopifySite,WebhookRequest

class WebhookInit:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session["webhook"] = None
        webhookId = None
        response = None
        if request.headers.get("X-Shopify-Topic"):

            webhookId = request.headers.get("X-Shopify-Event-Id")
            webhookRequest,created = WebhookRequest.objects.get_or_create(webhookId=webhookId)
            if not created:
                return HttpResponse(
                    content=json.dumps({"message":"duplicate request"}),
                    content_type="application/json",
                    status=409
                )
            try:
                shopifySite = ShopifySite.objects.get(
                    shopDomain=f"{request.headers["X-Shopify-Shop-Domain"]}.myshopify.com"
                )
                if ShopifySite.validateSignature(request):
                    request.session["webhook"] = {
                        "topic":request.headers.get("X-Shopify-Topic"),
                        "shop":request.headers.get("X-Shopify-Shop-Domain"),
                        "id":request.headers.get("X-Shopify-Event-Id"),
                    }
                    request.session["shopify"] = {
                        "shop_url":f"{shopifySite.shopDomain}",
                        "access_token":shopifySite.token()
                    }
                    shopifySite.startSession()
                response = self.get_response(request)
                webhookRequest.delete()
            except:
                pass
        else:
            response = self.get_response(request)
        return response