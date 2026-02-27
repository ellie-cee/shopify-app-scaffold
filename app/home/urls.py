from django.contrib import admin
from django.urls import path
import shopify_proxy.views as pviews
from . import views

urlpatterns = [
    path('', views.homePage),
    path('install',views.install),
    path("testemail",views.testEmail),
    path("shopify",views.dashboard),
]
