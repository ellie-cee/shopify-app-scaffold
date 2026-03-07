import os
import sys
from django.http import HttpResponse
from jmespath import search as jpath
import json
from dict_recursive_update import recursive_update
import logging
from django.template import RequestContext
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import traceback
from django.forms.models import model_to_dict
from django.db import models
import uuid
from datetime import datetime,date,timedelta
from decimal import Decimal


logger = logging.getLogger(__name__)

class EmailStatus:
    def __init__(self,success=True,message="succeeded"):
        self.success = success
        self.message = message
        


class Data:
    @staticmethod
    def jsonify(value):
        if isinstance(value,models.Model):
            return Data.jsonify(Data.modelToJson())
        elif isinstance(value,dict):
            ret = {}
            for key,value in value.items():
                if isinstance(value,Decimal):
                    ret[key] = float(value)
                elif isinstance(value,datetime):
                    ret[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value,date):
                    ret[key] = value.strftime("%Y-%m-%d")
                elif hasattr(value,'dict'):
                    return value.data
                else:
                    ret[key] = Data.jsonify(value)
            return ret
        elif isinstance(value,list):
            return [Data.jsonify(x) for x in value]
        elif isinstance(value,Searchable):
            return value.data
        else:
            return value
    @staticmethod
    def modelToJson(model):
        return model_to_dict(model)|{"id":str(model.id)}

class Searchable(object):

    def __init__(self,data):
        self.data = None
        if data is None:
            return None
        if isinstance(data,dict):
            data = Data.jsonify(data)
        self.data = data
    def dict(self):
        return self.data
    def valid(self):
        return self.data is not None
    def search(self,path,default=None):
        ret =  jpath(path,self.data)
        if ret is None:
            return default
        return ret
    def has(self,key):
        return hasattr(self,key)
    def get(self,key,default=None):
        if self.data is None:
            return None
        return self.data.get(key,default)
        
    def valueOf(self,key):
        ret = self.get(key)
        if ret is dict and self.search(f"{key}.refName"):
            return self.search(f"{key}.refName")
        else:
            return ret
    def dump(self,printIt=True,handle=sys.stdout):
        if printIt:
            print(json.dumps(self.data,indent=1),file=handle)
        else:
            return self.data
        
    def set(self,key,value):
        
        paths = list(reversed(key.split(".")))
        if isinstance(value,Searchable):
            value = value.data
        elif isinstance(value,list):
            value = [Data.jsonify(x) for x in value]
        elif isinstance(value,dict):
            value = Data.jsonify(value)
        if len(paths)>1:
            object = value
            for k in paths:
                object = {k:object}
            self.data = recursive_update(self.data,object)
        else:
            if self.data is not None:
                self.data[key] = value
    def getAsSearchable(self,key,default={}):
        val = self.search(key)
        if isinstance(val,list):
            return [Searchable(x) for x in val]
        if isinstance(val,dict):
            return Searchable(val)
        if val is None:
            return None
        return val
    
    def append(self,key,value):
        myValue = self.search(key,[])
        myValue.append(value)
        self.set(key,myValue)
        return
        if key not in self.data:
            self.data[key] = value
        elif type(self.data[key]) is not list:
            self.data[key] = [self.data[key],value]
        else:
            self.data[key].append(value)
    @staticmethod
    def fromList(list):
        return [Searchable(x) for x in list]
    def dumpField(self,path):
        ret = self.search(path)
        if ret is None:
            print("None")
        else:
            if isinstance(ret,dict) or isinstance(ret,list):
                print(json.dumps(ret,indent=1))
            else:
                print(ret)
                                
def sendEmail(recipient=None,subject="helloes",context={}, template=None,templatePrefix="base",sender=f'Eleanor Cassady <{os.environ.get("DEFAULT_EMAIL")}>',replyTo=None) ->EmailStatus:
    context["year"] = datetime.now().year   
    msg = EmailMultiAlternatives(
        subject,
        "this is a email",
        sender,
        [recipient],
        reply_to=[] if replyTo is None else [replyTo]
    )
    
    msg.attach_alternative(
        render_to_string(
            template if template is not None else f"email/{templatePrefix}.html",
            context
        ),
        "text/html"
    )
    try:
        msg.send()
        return EmailStatus()
    except:
        return EmailStatus(False,traceback.format_exc())

def modelToJson(model):
    return model_to_dict(model)|{"id":str(model.id)}

def jsonify(value):
        if isinstance(value,models.Model):
            return jsonify(modelToJson(value))
        elif isinstance(value,datetime):
            return str(value)
        elif isinstance(value,dict):
            ret = {}
            for key,value in value.items():
                if isinstance(value,uuid.UUID):
                    ret[key] = str(value)
                else:
                    ret[key] = jsonify(value)
            return ret
        elif isinstance(value,list):
            return [jsonify(x) for x in value]
        else:
            return value
    
def jsonResponse(payload,status=200):
    payload["status"] = status
    return HttpResponse(
        json.dumps(payload),
        content_type="application/json",
        status=status
    )