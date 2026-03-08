from django.urls import path

from . import views

urlpatterns = [
    path("uninstall",views.uninstall),
    path("compliance",views.compliance)
]
    