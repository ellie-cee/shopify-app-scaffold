from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ResumeVariant,SiteNav,Page,TextWithImage,Image
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline


class ContentTypeExcludedAdmin(admin.ModelAdmin):
    exclude=["content_type","object_id"]
@admin.register(ResumeVariant)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ( 'label',)
    search_fields = ('label',)



@admin.register(TextWithImage)
class TWIAdmin(ContentTypeExcludedAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)




class IWTInline(GenericStackedInline):
    model = TextWithImage
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        return extra
@admin.register(Page)
class PageAdmin(ContentTypeExcludedAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    exclude=["content_type"]
    inlines = [IWTInline]


