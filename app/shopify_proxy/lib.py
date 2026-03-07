import traceback
from django.shortcuts import render
from django.template import RequestContext
from .decorators import validProxy
from root.views import getJsonPayload,jsonResponse
from root.lmno import sendEmail
from logging import Logger
import os
from django.views.decorators.csrf import csrf_exempt

def getProxyDetails(request):
    rc = RequestContext(request)
    rc.get('proxyDetails')
