import os
import uuid
from django.db import models
from datetime import datetime,timedelta
import random
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

utc = pytz.UTC


# Create your models here.

class UserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,db_index=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "user_permission"


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,default="No Name")
    email = models.EmailField(db_index=True)
    permissions = models.ManyToManyField(UserPermissions)
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def hasPermission(self,permission):
        return True
        if self.permissions.filter(name=permission)>0:
            return True
        return False
    def createAuth(self,authRequest=None):
        if authRequest is None:
            authRequest = AuthRequest(
                requestUser=self,
                expires=datetime.now()+timedelta(minutes=60),
                
            )
        authRequest.code = AuthRequest.generateCode()
        authRequest.expires = datetime.now()+timedelta(minutes=60)
        authRequest.save()
        self.sendAuthEmail(authRequest)
        
        return authRequest
    def sendAuthEmail(self,authRequest):
        
        msg = EmailMultiAlternatives(
            "Your YWM Login Code",
            render_to_string(
                "authcode.txt",
                {
                    "authCode":authRequest.code,
                    "user":self
                }
            ),
            os.environ.get("DEFAULT_EMAIL"),
            [self.email],
        )
        msg.attach_alternative(
            render_to_string(
                "authcode.html",
                {
                    "authCode":authRequest.code,
                    "user":self
                }
            ),
            "text/html"
        )
        msg.send()
        
    def censoredEmail(self):
        return f"{self.email[0:3]}***@{self.email.split('@')[-1]}"
    class Meta:
        db_table="ywm_user"

class AuthRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    requestUser = models.ForeignKey(User,on_delete=models.CASCADE)
    code = models.CharField(max_length=64,db_index=True)
    expires = models.DateTimeField()
    
    @staticmethod
    def generateCode():
        return "".join([str(random.randint(0,9)) for x in range(6)])
    def isExpired(self):
        return self.expires.replace(tzinfo=utc)<datetime.now().replace(tzinfo=utc)
    def matches(self,supliedCode):
        return self.code==supliedCode
    
    class Meta:
        db_table="auth_request"