
import logging
from .models import SiteNav
import os


logger = logging.getLogger(__name__)
def sidebarNav(request):
    ret =  {
        "sidebarNav":SiteNav.objects.order_by("displayOrder").all()
    }
    
    
    return ret
def env(request):
    
    return {
        "env":dict(os.environ)
    }
    
def proxyDetails(request):
    return {
        "shopName":request.GET.get("shop"),
        "customerId":request.GET.get("logged_in_customer_id")
    }
