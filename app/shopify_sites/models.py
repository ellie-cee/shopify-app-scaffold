import os
from django.db import models
import hashlib, base64, hmac
from .graphql import GraphQL
import shopify
import sys
import hmac,hashlib
import logging
# Create your models here.
logger = logging.Logger(__name__)

class ShopifySite(models.Model):
    id = models.BigAutoField(primary_key=True)
    shopId = models.BigIntegerField(db_index=True,null=True,default=0)
    shopName = models.CharField(max_length=128,default="")
    shopDomain = models.CharField(max_length=64,default="",db_index=True)
    shopHost = models.CharField(max_length=255,default="",db_index=True)
    accessToken = models.CharField(max_length=255,default="")
    shopifyUrl = models.CharField(max_length=255,default="")
    contactName = models.CharField(max_length=255,default="")
    contactEmail = models.CharField(max_length=255,default="")
    
    def __str__(self):
        return self.shopName
    
    @staticmethod
    def validateSignature(request):
        params = request.GET.dict()
        
        signature = params.pop('signature')
        print(params)
        if signature is None:
            return False
        secret = os.environ.get("SHOPIFY_API_SECRET")
        line = ''.join([
            '%s=%s' % (key, value)
            for key, value in sorted(params.items())
        ])
        
        h = hmac.new(secret.encode('utf-8'), line.encode('utf-8'), hashlib.sha256)
        print(h.hexdigest())
        if hmac.compare_digest(h.hexdigest(), signature) == False:
            return False
        return True
    
    @staticmethod
    def load(domain):
        try:
            profile = ShopifySite.objects.get(shopifyDomain=domain)
            profile.startSession()
        except:
            print(f"Unable to load profile {domain}",file=sys.stderr)
            return None
        
    def startSession(self):
        shopify.ShopifyResource.activate_session(
            shopify.Session(
                f"{self.shopDomain}/admin",
                os.environ.get("API_VERSION"),
                self.accessToken
            )
        )
    def shopDetails(self):
        self.startSession()
        shop = GraphQL().run(
            """
            query {
                shop {
                    id
                    contactEmail
                    url
                    shopOwnerName
                    name
                    myshopifyDomain
                    primaryDomain {
                        host
                        url
                    }
                }
                
            }
            """,
            {}
        
        )
        if shop.isUnauthorized():
            return False
        self.shopId = int(shop.search("data.shop.id","").split("/")[-1])
        self.shopHost = shop.search("data.shop.primaryDomain.host","")
        self.contactEmail = shop.search("data.shop.contactEmail")
        self.contactName = shop.search("data.shop.shopOwnerName")
        self.shopName = shop.search("data.shop.name ")
        self.shopUrl = shop.search("data.shop.url")
        self.save()
        return True
        
    
    class Meta:
        db_table = "shopifySite"
    def tld(self):
        return f"{self.shopDomain}.myshopify.com"
