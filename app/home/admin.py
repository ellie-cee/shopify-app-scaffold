from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ResumeVariant,SiteNav

@admin.register(ResumeVariant)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ( 'label',)
    search_fields = ('label',)
@admin.register(SiteNav)
class SiteNavAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)
