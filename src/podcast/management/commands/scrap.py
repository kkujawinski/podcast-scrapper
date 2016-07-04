import json
import logging
import os
import re
import time
from datetime import timedelta

import boto3
import boto3.session
from boto3.s3.transfer import S3Transfer
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.utils.functional import cached_property
from lxml import etree
from podcast.models import (Podcast, PodcastIgnoreItem, PodcastItem,
                            PodcastScrapingConfiguration)
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from temp_utils.contextmanagers import temp_file

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrap podcasts'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        log.debug('Initializing headless Firefox')
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        caps = DesiredCapabilities.FIREFOX
        caps["marionette"] = True
        caps["binary"] = "/usr/bin/firefox"
        self.browser = webdriver.Firefox(capabilities=caps)
        log.debug('Initialized headless Firefox')

    def __del__(self):
        self.browser.quit()
        self.display.stop()

    def add_arguments(self, parser):
        parser.add_argument('podcast', nargs='*')

    def get_podcasts_config(self, options):
        if options['podcast']:
            for podcast_config in options['podcast']:
                try:
                    yield PodcastScrapingConfiguration.objects.get(pk=podcast_config)
                except PodcastScrapingConfiguration.DoesNotExist:
                    raise CommandError('Podcast "%s" is not configured' % podcast_config)
        else:
            for podcast in PodcastScrapingConfiguration.objects.filter():
                yield podcast

    def scrap_value_items(self, type_, value_config, document):
        if type_ == 'xpath':
            page_source = self.browser.page_source
            page_source = re.sub('xmlns(:\w+)?="[^"]+"', '', page_source)
            page_source = BeautifulSoup(page_source, 'lxml')
            parser = etree.XMLParser(recover=True)
            document = etree.fromstring(str(page_source), parser)

            def get_text(d):
                try:
                    output = ''.join(d.itertext())
                except AttributeError:
                    output = d
                return output.strip()

            return [get_text(d) for d in document.xpath(value_config['xpath'])]
        elif type_ == 'json':
            return [value_config['value'].format(**json.loads(d)) for d in document]
        elif type_ == 'regex' and 'replace' in value_config:
            return [re.sub(value_config['search'], value_config['replace'], d) for d in document]
        elif type_ == 'regex':
            return [re.search(value_config['search'], d).groups() for d in document]
        elif type_ == 'format':
            return [value_config['format'].format(*d) for d in document]
        elif type_ == 'join':
            sep = value_config.get('sep', '')
            return [sep.join(document)]
        elif type_ == 'const':
            return [value_config['value']]
        elif type_ == 'timedelta':
            parsed = [re.match(value_config['format'], d).groupdict() for d in document]
            parsed = [{k: int(v) for k, v in p.items()} for p in parsed]
            return [timedelta(**p) for p in parsed]
        elif type_ == 'OR':
            for item in value_config['items']:
                scrapped_value = self.scrap_values(item)
                if scrapped_value:
                    return scrapped_value

    def scrap_values(self, value_config, document=None):
        if isinstance(value_config, list):
            scrapped_value = document
            for value_config_item in value_config:
                scrapped_value = self.scrap_values(value_config_item, scrapped_value)
            return scrapped_value
        elif isinstance(value_config, dict):
            return self.scrap_value_items(value_config['type'], value_config, document)
        else:
            return self.scrap_value_items('xpath', {'xpath': value_config}, document)

    def scrap_podcast(self, steps, **params):
        PODCAST_FIELDS = ['title', 'description', 'language', 'image_url']
        for field in PODCAST_FIELDS:
            field_steps = steps['store'][field]
            params[field] = self.scrap_values(field_steps)[0]
        return Podcast.objects.create(**params)

    def scrap_podcast_item(self, steps, **params):
        PODCAST_ITEM_FIELDS = ['title', 'description', 'audio_url', 'audio_duration', 'pub_date', ]
        for field in PODCAST_ITEM_FIELDS:
            field_steps = steps['items-store'][field]
            try:
                value = self.scrap_values(field_steps)[0]
            except IndexError:
                pass
            else:
                if value:
                    params[field] = value
        return PodcastItem.objects.create(**params)

    def process_next_items_page(self, steps):
        try:
            next_page_link = self.browser.find_element_by_xpath(steps['items-next_page'])
        except NoSuchElementException:
            return
        else:
            log.debug('Opening next page')
            next_page_link.click()
            return True

    def get_podcast_page_items_urls(self, steps):
        items = self.scrap_values(steps['items-steps'])
        log.debug("Fetched %d items urls" % len(items))
        return items

    def get_podcast_all_items_urls(self, steps):
        items = []
        while True:
            items.extend(self.get_podcast_page_items_urls(steps))

            if not self.process_next_items_page(steps):
                break
            time.sleep(1.5)
        return items

    @cached_property
    def _s3_transfer_client(self):
        session = boto3.session.Session(region_name=os.environ['AWS_REGION_NAME'])
        session_config = boto3.session.Config(signature_version=os.environ['AWS_SIGNATURE_VERSION'])
        s3client = session.client('s3', config=session_config)
        return S3Transfer(s3client)

    def publish_to_aws(self, podcast):
        transfer = self._s3_transfer_client
        with temp_file() as file_path:
            with open(file_path, 'wb') as f:
                f.write(podcast.generate_rss())
            public_url = podcast.config.get_path()
            transfer.upload_file(
                file_path, os.environ['AWS_BUCKET'],
                public_url,
                extra_args={'ACL': 'public-read', 'ContentType': 'application/xml'}
            )
            log.info('Published RSS to %s' % public_url)

    def publish_index_to_aws(self):
        transfer = self._s3_transfer_client
        podcasts_configs = PodcastScrapingConfiguration.objects.select_related('podcast').filter(podcast__isnull=False)
        template = loader.get_template('index.html')
        context = {
            'podcasts_configs': podcasts_configs,
        }
        with temp_file() as file_path:
            with open(file_path, 'w') as f:
                f.write(template.render(context))
            transfer.upload_file(
                file_path, os.environ['AWS_BUCKET'],
                'index.html',
                extra_args={'ACL': 'public-read', 'ContentType': 'text/html; charset=UTF-8'}
            )
            log.info('Published new index.html')

    def handle(self, *args, **options):
        any_changed = False
        for podcast_config in self.get_podcasts_config(options):
            start_url = podcast_config.start_url
            steps = podcast_config.steps.steps
            changed = False

            try:
                self.browser.get(start_url)

                try:
                    podcast = podcast_config.podcast
                except Podcast.DoesNotExist:
                    podcast = self.scrap_podcast(steps, link=start_url, config=podcast_config)

                podcast_items_urls = set(podcast.items.values_list('link', flat=True))
                podcast_items_ignore_urls = set(podcast.ignore_items.values_list('link', flat=True))
                items_urls = self.get_podcast_all_items_urls(steps)
            except:
                log.error('Failed scrapping podcast details')

            for item_url in items_urls:
                if item_url in podcast_items_urls:
                    log.debug('Skipped %s' % item_url)
                    continue
                if item_url in podcast_items_ignore_urls:
                    log.debug('Ignored %s' % item_url)
                    continue

                log.info('Processing [%s] %s' % (podcast_config.slug, item_url))
                try:
                    self.browser.get(item_url)
                    self.scrap_podcast_item(steps, link=item_url, podcast=podcast)
                except:
                    PodcastIgnoreItem.objects.create(podcast=podcast, link=item_url)
                    log.exception('Failed scrapping url %s ' % self.browser.current_url)
                else:
                    changed = True
                    any_changed = True

            if changed:
                self.publish_to_aws(podcast)

        if any_changed:
            self.publish_index_to_aws()
