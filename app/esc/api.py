import requests
import shopify
from .data import Searchable
import pathlib
import os
import json
import datetime


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
PROFILES = pathlib.Path(os.path.join(BASE_DIR,".shopify_profiles.json"))
API_VERSION = "2026-01"


class ShopifyAPI:
    def __init__(self):
        self.profiles:Searchable
        if PROFILES.exists():
            self.profiles = self.read()
        else:
            self.profiles = Searchable(
                {
                    "default":{}
                }
            )
            self.write()
    def read(self):
        return Searchable(
            json.load(
                open(PROFILES)
            )
        )
    def add(self,name,details):
        self.profiles.set(name,details)
    def write(self):
        
        with open(PROFILES,"w") as file:
            json.dump(self.profiles.dict(),file)    
    def set(self,name="default",key=None,value=None):
        self.profiles.set(f"{name}.{key}",value)
        self.write()
    def get(self,name,key,default=None):
        return self.profiles.search(f"{name}.{key}",default)
    def expires(self,name):
        return self.get(name,"expires")
    def shop(self,name):
        return self.get(name,"shop")
    def shopifyDomain(self,name):
        return f"{self.shop(name)}.myshopify.com"
    def adminURL(self,name):
        return f"{self.shop(name)}.myshopify.com/admin"
    def id(self,name):
        return self.get(name,"clientId")
    def secret(self,name):
        return self.get(name,"clientSecret")
    def token(self,name):
        token = self.get(name,"token")
        expires = self.get(name,"expires")
        now = int(datetime.datetime.now().timestamp())
        if now>self.get(name,"expires",0):
            grant = requests.post(
                f"https://{self.adminURL(name)}/oauth/access_token",
                headers={
                    "Content-Type":"application/x-www-form-urlencoded"
                },
                data={
                    "grant_type":"client_credentials",
                    "client_id":self.id(name),
                    "client_secret":self.secret(name)
                }
            ).json()
            token = grant.get("access_token")
            self.set(name,"expires",now+grant.get("expires_in"))
            self.set(name,"token",token)
        return token
    @staticmethod
    def load(name="default"):
        profiles = ShopifyAPI()
        shopify.ShopifyResource.activate_session(
            shopify.Session(
                profiles.adminURL(name),
                API_VERSION,
                profiles.token(name)
            )
        )





