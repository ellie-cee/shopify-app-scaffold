from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [
    path("auth/login/status",views.loginStatus),
    path("auth/login/restart",views.loginStatus),
    path('auth/login', views.login),
    path("auth/code/validate",views.validate),
    path('auth/code/resend',views.resend),
    path('auth/code/restart',views.resend),
    path("logout",views.logout)
]
