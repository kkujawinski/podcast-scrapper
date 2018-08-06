import importlib

from django.conf import settings
from django.http.response import Http404


class SubdomainMiddleware:
    def process_request(self, request):
        """Parse out the subdomain from the request"""
        request.subdomain = None
        host = request.META.get('HTTP_HOST', '')
        host_s = host.replace('www.', '').split('.')
        path = request.path[1:]

        if len(host_s) > 1:
            subdomain = host_s[0]
            if subdomain not in settings.SUBDOMAINS:
                return

            patterns = importlib.import_module('core.' + subdomain + '_url').urlpatterns
            for pattern in patterns:
                if pattern.resolve(path):
                    break
            else:
                raise Http404()
