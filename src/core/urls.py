# coding: utf-8
from django.conf import settings
from django.conf.urls import url

from .admin_url import urlpatterns as admin_urlpatterns
from .api_url import urlpatterns as api_urlpatterns
from .views import IndexView

urlpatterns = api_urlpatterns + admin_urlpatterns

if settings.DEBUG:
    urlpatterns += [url(r'^index/$', IndexView.as_view())]
