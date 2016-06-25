import json
import re
from pyvirtualdisplay import Display
from selenium import webdriver

from django.core.management.base import BaseCommand, CommandError
from podcast.models import PodcastScrapingConfiguration


class Command(BaseCommand):
    help = 'Scrap podcasts'

    def add_arguments(self, parser):
        parser.add_argument('podcast', nargs='+')

    def get_podcasts(self, options):
        for podcast_config in options['podcast']:
            try:
                yield PodcastScrapingConfiguration.objects.get(pk=podcast_config)
            except PodcastScrapingConfiguration.DoesNotExist:
                raise CommandError('Podcast "%s" is not configured' % podcast_config)

    def scrap_value_item(self, type_, value_config, document):
        if type_ == 'xpath':
            pass
        elif type_ == 'json':
            return value_config['value'].format(**json.loads(document))
        elif type_ == 'regex':
            return re.replace(value_config['search'], value_config['replace'])
        elif type_ == 'const':
            return value_config['value']

    def scrap_value(self, value_config, document):
        if isinstance(value_config, list):
            scrapped_value = document
            for value_config_item in value_config:
                scrapped_value = self.scrap_value(value_config_item, scrapped_value)
            return scrapped_value
        elif isinstance(value_config, dict):
            return self.scrap_value_item(value_config['type'], value_config, document)
        else:
            return self.scrap_value_item('xpath', {'xpath': value_config}, document)

    def scrap_podcast(self, podcast_config, document):
        pass

    def scrap_items(self, podcast_items_config, document):
        pass

    def process_next_page(self, next_page_config, document):
        pass

    def handle(self, *args, **options):
        for podcast_config in self.get_podcasts_config(options):
            podcast = podcast_config.podcast
            document = ''

            display = Display(visible=0, size=(1024, 768))
            display.start()
            driver = webdriver.Firefox()
            driver.get("http://www.wp.pl")

            if podcast is None:
                podcast = self.scrap_podcast(podcast_config, document)

            while document is not None:
                items = self.scrap_items(podcast_config['items'], document)
                document = self.process_next_page(podcast_config['next_page'], document)
