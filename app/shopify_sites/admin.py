from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ShopifySite
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline


@admin.register(ShopifySite)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ( 'shopName',)
    search_fields = ('shopName','shopDomain',)
    exclude = ('accessToken','accessTokenExpires','shopId',)
