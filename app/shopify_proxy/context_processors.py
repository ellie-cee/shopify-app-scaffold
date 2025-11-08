

def proxyDetails(request):
    return {
        "shopName":request.GET.get("shop"),
        "customerId":request.GET.get("logged_in_customer_id"),
        "signature":request.get("signature")
    }