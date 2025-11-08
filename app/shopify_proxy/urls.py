from django.contrib import admin
from django.urls import path
from  . import views

urlpatterns = [
    path("",views.index),
    
    path("test",views.test),
    path("contact/send",views.sendContact),
    path("contact",views.contactForm)
]
