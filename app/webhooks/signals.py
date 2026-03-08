from django.db.models.signals import post_save,pre_delete
from django.core.signals import request_finished

from django.dispatch import receiver
from .models import Webhook

@receiver(post_save,sender=Webhook)
def created(sender,instance:Webhook,created,**kwargs):
    if created:
        instance.install()

@receiver(pre_delete,sender=Webhook)
def deleted(sender,instance:Webhook,using,origin,**kwargs):
    instance.uninstall()


        