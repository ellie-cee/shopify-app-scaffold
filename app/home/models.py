import uuid
from django.db import models
import os
import random
import pymupdf
from xyz import settings
import datetime
import logging
from slugify import slugify
from shopify_sites.graphql import GraphQL
from shopify_sites.models import ShopifySite
import shopify

logger = logging.Logger(__name__)


# Create your models here.

class IdAware:
    def getId(self):
        return str(self.id)

class SiteNav(models.Model,IdAware):
    id = models.BigAutoField(primary_key=True)
    #permission = models.CharField(max_length=64)
    url = models.CharField(max_length=255,default="/")
    label = models.CharField(max_length=255)
    displayOrder = models.IntegerField(default=99999999 )
    
    def __str__(self):
        return self.url
    
    
    
    class Meta:
        db_table="sitenav"
    
    