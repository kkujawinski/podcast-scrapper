# coding: utf-8
# Core and 3th party packages
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home.html"


class UrlsApi(APIView):
    def get(self, request, format=None):
        return Response({'admin_index': reverse('admin:index')})
