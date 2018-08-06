# coding: utf-8
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from podcast.models import PodcastScrapingConfiguration, PodcastSuggestion
from django.db.utils import IntegrityError


class SendSuggestionView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendSuggestionView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            PodcastSuggestion.objects.create(email=request.POST['email'], url=request.POST['url'])
        except IntegrityError as e:
            return HttpResponseBadRequest(str('Suggestion was already sent.'))
        except Exception as e:
            return HttpResponseBadRequest(str(e))
        return JsonResponse({})


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        return PodcastScrapingConfiguration.objects.get_index_context()
