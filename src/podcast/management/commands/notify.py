import logging
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.management.base import BaseCommand

from podcast.models import Podcast

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrapped podcasts summary chart'

    def handle(self, *args, **options):
        template_html = 'email_podcast_scrapping_summary.html'
        podcasts = Podcast.objects.all().order_by('title')

        to = 'kamil+podcastscrapper@kujawinski.net'
        from_email = 'dev@kujawinski.net'
        subject = "Podcast scrapping summary %s" % str(date.today())

        text_content = 'HTML version contains history charts'
        html_content = render_to_string(template_html, {"podcasts": podcasts})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
