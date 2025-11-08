import shopify
import logging

logger = logging.getLogger(__name__)
def current_shop(request):
    if not shopify.ShopifyResource.site:
        return {'current_shop': None}
    try:
        return {'current_shop': shopify.Shop.current()}
    except:
        return {'current_shop': None}
