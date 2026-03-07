from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import SiteNav,Config,ShopifyNav
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline


class ContentTypeExcludedAdmin(admin.ModelAdmin):
    exclude=["content_type","object_id"]

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ( 'key',)
    search_fields = ('key','value',)

@admin.register(SiteNav)
class SiteNavAdmin(admin.ModelAdmin):
    list_display = ( 'path','label',)
    search_fields = ('path','label')

@admin.register(ShopifyNav)
class ShopifyNavAdmin(admin.ModelAdmin):
    list_display = ( 'path','label',)
    search_fields = ('path','label')
