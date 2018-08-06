from django.conf.urls import url
from .views import SendSuggestionView

urlpatterns = [
    url(r'^suggestion/$', SendSuggestionView.as_view(), name='suggestion'),
]
