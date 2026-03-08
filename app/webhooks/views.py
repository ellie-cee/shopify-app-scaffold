from django.shortcuts import render
from .decorators import valid_webhook
from root import lmno
# Create your views here.

@valid_webhook
def uninstall(request):
    pass

@valid_webhook
def compliance(request):
    returnPayload = lmno.jsonResponse(
        {
            "message":"invalid topic",
        },
        status=200
    )
    match(request.session["webhook"].get("topic")):
        case "customers/data_request":
            returnPayload =  customersDataRequest(request)
        case "customers/redact":
            returnPayload =  customersRedact(request)
        case "shop/redact":
            returnPayload =  shopRedact(request)
    return returnPayload
        
def customersRedact(request):
    pass


def customersDataRequest(request):
    pass


def shopRedact(request):
    pass



