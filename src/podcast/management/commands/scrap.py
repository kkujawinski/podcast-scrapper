import contextlib
import json
import logging
import os
import re
import time
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils.functional import cached_property
from django.utils import timezone

import fcntl
from bs4 import BeautifulSoup
from lxml import etree
from podcast.models import (Podcast, PodcastIgnoreItem, PodcastItem,
                            PodcastScrapingConfiguration, s3_transfer_client)
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

log = logging.getLogger(__name__)

SCRAP_RETRIES = 3

class Command(BaseCommand):
    help = 'Scrap podcasts'

    @contextlib.contextmanager
    def init_browser(self):
        os.environ['PATH'] = '/opt/firefox/:' + os.environ['PATH']
        log.info('Initializing headless Firefox')

        display = Display(visible=0, size=(1024, 768))
        display.start()
        caps = DesiredCapabilities.FIREFOX
        caps["marionette"] = True
        caps["binary"] = "/opt/firefox/firefox"
        self.browser = webdriver.Firefox(capabilities=caps)
        self.browser.set_page_load_timeout(100)
        log.info('Initialized headless Firefox')
        yield
        self.browser.quit()
        display.stop()
        os.unlink('geckodriver.log')
        log.info('Headless Firefox cleaned up')

    @contextlib.contextmanager
    def lock(self):
        with open('/data/scraper_exclusive_lock', "wb") as f:
            log.info('Acquiring lock')
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
            fcntl.lockf(f, fcntl.LOCK_UN)
            log.info('Released lock')

    def refresh_document(self):
        page_source = self.browser.page_source
        page_source = re.sub('xmlns(:\w+)?="[^"]+"', '', page_source)
        page_source = BeautifulSoup(page_source, 'lxml')
        parser = etree.XMLParser(recover=True)
        self.document = etree.fromstring(str(page_source), parser)

    def browser_open_url(self, url):
        log.info('Opening url %s', url)
        if url[0] == '/':
            current_url = self.browser.current_url
            url = '/'.join(current_url.split('/', 3)[:3]) + url

        for i in range(1, SCRAP_RETRIES + 1):
            try:
                self.browser.get(url)
            except TimeoutException:
                log.info('TimeoutException')
                break
            except Exception as e:
                if i == SCRAP_RETRIES:
                    log.exception('Couldn\'t open')
                continue
            else:
                break
        else:
            raise Exception('Failed browser.get %d retries' % SCRAP_RETRIES)

        log.info('Opening url 3 %s', url)
        self.refresh_document()

    def add_arguments(self, parser):
        parser.add_argument('--podcast', action='append')
        parser.add_argument('--batch',  type=int)
        parser.add_argument('--batch-interval',  type=int)
        parser.add_argument('--url',  type=str)

    def get_podcasts_config(self, options):
        if options['url'] and not options['podcast']:
            podcast = PodcastScrapingConfiguration.objects.get(
                podcast__ignore_items__link=options['url']
            )
            yield podcast
        # elif options['url'] and options['podcast']:
        #         yield podcast
        elif options['podcast']:
            for podcast_config in options['podcast']:
                try:
                    yield PodcastScrapingConfiguration.objects.get(slug=podcast_config)
                except PodcastScrapingConfiguration.DoesNotExist:
                    raise CommandError('Podcast "%s" is not configured' % podcast_config)
        elif options['batch']:
            items = PodcastScrapingConfiguration.objects.get_least_recently_updated(
                 interval=timedelta(days=options['batch_interval']), limit=options['batch']
            )
            for podcast in items:
                yield podcast
        else:
            for podcast in PodcastScrapingConfiguration.objects.filter():
                yield podcast

    def scrap_value_items(self, type_, value_config, document):
        if type_ == 'xpath':
            def get_text(d):
                try:
                    output = ''.join(d.itertext())
                except AttributeError:
                    output = d
                return output.strip()
            return [get_text(d) for d in self.document.xpath(value_config['xpath'])]
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
            try:
                params[field] = self.scrap_values(field_steps)[0]
            except:
                pass
        return Podcast.objects.create(**params)

    def scrap_podcast_item(self, steps, **params):
        PODCAST_ITEM_FIELDS = ['title', 'description', 'audio_url', 'audio_duration',]
        for field in PODCAST_ITEM_FIELDS:
            log.info('Scrap podcast field %s 1' % field)
            field_steps = steps['items-store'][field]
            log.info('Scrap podcast field %s 2' % field)
            try:
                value = self.scrap_values(field_steps)[0]
            except (IndexError, TypeError):
                pass
            else:
                log.info('Scrap podcast field %s 3' % field)
                if value:
                    params[field] = value
                    log.info('Scrapped podcast field %s=%s' % (field, value))
        log.info('Creating podcast item %s' % str(params))
        item = PodcastItem.objects.create(**params)
        log.info('Creating podcast item 2 %s' % str(params))
        PodcastIgnoreItem.objects.filter(podcast=params['podcast'], link=params['link']).delete()
        log.info('Creating podcast item 3')
        return item

    def process_next_items_page(self, steps):
        try:
            next_page_link = self.browser.find_element_by_xpath(steps['items-next_page'])
        except NoSuchElementException:
            return
        else:
            log.info('Opening next page')
            next_page_link.click()
            self.refresh_document()
            return True

    def get_podcast_page_items_urls(self, steps):
        items = self.scrap_values(steps['items-steps'])
        log.info("Fetched %d items urls" % len(items))
        items = [item for item in items if ':' not in item or item.split(':')[0] in ('http', 'https')]
        return items

    def get_podcast_all_items_urls(self, steps):
        items = set()
        items_len = 0

        while True:
            items.update(self.get_podcast_page_items_urls(steps))
            items_len_new = len(items)
            if not self.process_next_items_page(steps) or items_len == items_len_new:
                break
            items_len = items_len_new
            time.sleep(1.5)
        return items

    @cached_property
    def _s3_transfer_client(self):
        return s3_transfer_client()

    def handle(self, *args, **options):
        podcast_config_items = list(self.get_podcasts_config(options))
        if not podcast_config_items:
            log.info('No podcast config items to process')

        try:
            with self.lock():
                with self.init_browser():
                    self._handle(podcast_config_items, options)
        except BlockingIOError:
            log.info('Another scraper process is running')
            exit(0)

    def _handle(self, podcast_config_items, options):
        any_changed = False
        for podcast_config in podcast_config_items:
            changed = False
            steps = podcast_config.steps.steps

            if options['url']:
                podcast = podcast_config.podcast
                link = options['url']
                items_urls = [link]
                deleted = podcast.items.filter(link=link).delete()[1]
                deleted.update(podcast.ignore_items.filter(link=link).delete()[1])

                log.info('Deleted items %s' % deleted)
            else:
                start_url = podcast_config.start_url
                log.info('Processing podcast %s' % start_url)

                try:
                    self.browser_open_url(start_url)
                    try:
                        podcast = podcast_config.podcast
                    except Podcast.DoesNotExist:
                        podcast = self.scrap_podcast(steps, link=start_url, config=podcast_config)

                    items_urls = self.get_podcast_all_items_urls(steps)
                except:
                    log.exception('Failed scrapping podcast details %s' % podcast_config.slug)
                    continue

            podcast_items_urls = set(podcast.items.values_list('link', flat=True))
            omit_threshold = timezone.now() - timedelta(days=5)
            podcast_items_ignore_urls = set(
                podcast.ignore_items.filter(ignore_date__lt=omit_threshold).values_list('link', flat=True)
            )

            for item_url in items_urls:
                if item_url in podcast_items_urls:
                    log.info('Skipped %s' % item_url)
                    continue
                if item_url in podcast_items_ignore_urls:
                    log.info('Ignored %s' % item_url)
                    continue

                log.info('Processing [%s] %s' % (podcast_config.slug, item_url))
                try:
                    self.browser_open_url(item_url)
                    log.info('Processing 1 [%s] %s' % (podcast_config.slug, item_url))
                    self.scrap_podcast_item(steps, link=item_url, podcast=podcast)
                    log.info('Processing 2 [%s] %s' % (podcast_config.slug, item_url))
                except:
                    log.info('Processing failed [%s] %s' % (podcast_config.slug, item_url))
                    obj, created = PodcastIgnoreItem.objects.get_or_create(
                        podcast=podcast, link=item_url)
                    if created:
                        log.exception('Failed scrapping url %s' % self.browser.current_url)
                    else:
                        log.exception('Failed scrapping url %s, first_failure %s' % (
                            self.browser.current_url, obj.ignore_date))
                else:
                    changed = True
                    any_changed = True

            log.info('Podcast touch')
            podcast_config.touch()

            if changed:
                public_url = podcast.publish_to_aws(self._s3_transfer_client)
                log.info('Published RSS to %s' % public_url)

        if any_changed:
            PodcastScrapingConfiguration.objects.publish_index_to_aws(self._s3_transfer_client)
            log.info('Published new index.html')
