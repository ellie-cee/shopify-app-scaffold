from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='shopify_sites_login'),
    path('authenticate', views.authenticate, name='shopify_sites_authenticate'),
    path('finalize', views.finalize, name='shopify_sites_login_finalize'),
    path('logout', views.logout, name='shopify_sites_logout'),
]
