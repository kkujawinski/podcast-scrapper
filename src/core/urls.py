# coding: utf-8
# Core and 3th party packages
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'', include(admin.site.urls)),
    # add api urls and allow to be passed only them in certain domains
    # they can't overlap with admin
]

# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.i18n import javascript_catalog

# # Project imports
# from .views import HomePageView, UrlsApi

# urlpatterns = [
#     url(r'^$', HomePageView.as_view(), name='home'),
#     url(r'^admin/', include(admin.site.urls)),
#     url(r'^api-auth/', include('rest_framework.urls',
#         namespace='rest_framework')),
#     url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
#     url(r'^api/urls/$', UrlsApi.as_view(), name='api_urls'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
