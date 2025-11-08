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

class BaseModel(models.Model):
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
class ResumeVariant(models.Model):
    type = models.CharField(max_length=255,default="")       
    label = models.CharField(max_length=255,default="")

    class Meta:
        db_table = "resumeVariants"

class ApplicationVariant(models.Model):
    id = models.BigAutoField(primary_key=True)
    identifier = models.CharField(default="",max_length=255)
    name = models.CharField(max_length=255)
    details = models.TextField(default="")
    purged = models.BooleanField(default=False)
    filePath = models.CharField(max_length=255,default="")
    active = models.BooleanField(default=True)
    
    def process(self,variant):
        employerTag = slugify(self.name)
        self.identifier = employerTag
        outputFileSuffix = f"{datetime.datetime.now().strftime("%Y-%m-%d")}-{employerTag}"
        outputFileName = f"eleanor-cassady-{outputFileSuffix}.pdf"
        
        
        outputFile = inputFile = os.path.join(
            settings.FILES_ROOT,
            "ephemeral",
            outputFileName
        )
        self.filePath = outputFile
        self.save()
        logger.error(["shopify",shopify])
        document = pymupdf.open(
            os.path.join(
                settings.FILES_ROOT,
                "docs",
                f"resume-template-{variant}.pdf"
            )
        )
        
        ret = GraphQL().run(
            """
            mutation addUrlRedirect($urlRedirect:UrlRedirectInput!) {
                urlRedirectCreate(urlRedirect:$urlRedirect) {
                    urlRedirect {
                        id
                        path
                        target
                    }
                }
            }
            """,
            {
                "urlRedirect":{
                    "path":f"/inquiries/{self.identifier}",
                    "target":f"/?inquirer={self.identifier}"
                }
            }
        )
        if ret.hasErrors():
            print(ret.errorMessages())
            
        for page in document:
            for link in page.get_links():
                
                if os.environ.get("SHOPIFY_DOMAIN") in link.get("uri"):
                    link["uri"] = f"https://{os.environ.get('SHOPIFY_DOMAIN')}/inquiries/{self.identifier}"
                    page.update_link(link)
        document.save(outputFile)
        return outputFile,outputFileName
    
    