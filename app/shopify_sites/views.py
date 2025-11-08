import json
import traceback
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import RequestContext
from django.apps import apps
import hmac, base64, hashlib, binascii, os
import logging
import shopify



logger = logging.Logger(__name__)


def _new_session(shop_url):
    api_version = apps.get_app_config('shopify_sites').SHOPIFY_API_VERSION
    session = shopify.Session(shop_url, api_version)
    return session

# Ask user for their ${shop}.myshopify.com address
def login(request):
    # If the ${shop}.myshopify.com address is already provided in the URL,
    # just skip to authenticate
    if request.GET.get('shop'):
        return authenticate(request)
    
    return render(request, 'shopify_login.html', {})

def authenticate(request):
    shop_url = request.GET.get('shop', request.POST.get('shop')).strip()
    if not shop_url:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    
    scope = apps.get_app_config('shopify_sites').SHOPIFY_API_SCOPE
    redirect_uri = request.build_absolute_uri(reverse(finalize))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    request.session['shopify_oauth_state_param'] = state
    permission_url = _new_session(shop_url).create_permission_url(redirect_uri,scope,state)
    return redirect(permission_url)

def finalize(request):
    api_secret = os.environ.get("SHOPIFY_API_SECRET") #apps.get_app_config('shopify_sites').SHOPIFY_API_SECRET
    params = request.GET.dict()
    
    logger.error(params)
    logger.error(f"\n\n{api_secret}\n\n")
        
    if request.session['shopify_oauth_state_param'] != params['state']:
        logger.error('Anti-forgery state token does not match the initial request.')
        return redirect(reverse(login))
    else:
        request.session.pop('shopify_oauth_state_param', None)

    myhmac = params.pop('hmac')
    line = '&'.join([
        '%s=%s' % (key, value)
        for key, value in sorted(params.items())
    ])
    h = hmac.new(api_secret.encode('utf-8'), line.encode('utf-8'), hashlib.sha256)
    if hmac.compare_digest(h.hexdigest(), myhmac) == False:
        logger.error("Could not verify a secure login")
        return redirect(reverse(login))

    try:
        shop_url = params['shop']
        session = _new_session(shop_url)
        logger.error(f"\n\n{session.secret}\n\n")
        request.session['shopify'] = {
            "shop_url": shop_url,
            "access_token": session.request_token(request.GET)
        }
        
            
    except Exception as e:
        traceback.print_exc()
        logger.error("Could not log in to Shopify store.")
        return redirect(reverse(login))
    
    messages.info(request, "Logged in to shopify store.")
    
    return redirect("/install")

def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))
