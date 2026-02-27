import os
import traceback
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
from django.http import FileResponse
import datetime
import random
logger = logging.Logger(__name__)
import pathlib
import logging 

logger = logging.Logger(__name__)