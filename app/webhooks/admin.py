from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(WebhookDefinition)
class WebhookDefinitionAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label','topic')

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('site__shopName','topic')
    search_fields = ('site__shopName','site__shopDomain','topic')
