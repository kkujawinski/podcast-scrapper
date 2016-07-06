import datetime
import os
import time
import urllib.request
from xml.etree import ElementTree as ET

import boto3
import boto3.session
from boto3.s3.transfer import S3Transfer
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template import loader
from email.utils import formatdate, parsedate
from temp_utils.contextmanagers import temp_file

ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
ET.register_namespace('itunes', ITUNES_NS)


def s3_transfer_client():
    session = boto3.session.Session(region_name=os.environ['AWS_REGION_NAME'])
    session_config = boto3.session.Config(signature_version=os.environ['AWS_SIGNATURE_VERSION'])
    s3client = session.client('s3', config=session_config)
    return S3Transfer(s3client)


class PodcastScrapingSteps(models.Model):
    name = models.CharField(max_length=50)
    steps = JSONField()

    class Meta:
        verbose_name = "Podcast scraping steps"
        verbose_name_plural = "Podcast scraping steps"

    def scrap(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'PodcastScrapingSteps<%s>' % str(self)


class PodcastScrapingConfigurationManager(models.Manager):
    def publish_index_to_aws(self, transfer_client=None):
        if transfer_client is None:
            transfer_client = s3_transfer_client()
        podcasts_configs = PodcastScrapingConfiguration.objects.\
            select_related('podcast').filter(podcast__isnull=False).\
            order_by('podcast__title')

        template = loader.get_template('index.html')
        context = {
            'podcasts_configs': podcasts_configs,
        }
        with temp_file() as file_path:
            with open(file_path, 'w') as f:
                f.write(template.render(context))
            transfer_client.upload_file(
                file_path, os.environ['AWS_BUCKET'],
                'index.html',
                extra_args={'ACL': 'public-read', 'ContentType': 'text/html; charset=UTF-8'}
            )


class PodcastScrapingConfiguration(models.Model):
    objects = PodcastScrapingConfigurationManager()

    steps = models.ForeignKey('PodcastScrapingSteps')
    slug = models.CharField(max_length=50, unique=True)
    start_url = models.URLField()

    class Meta:
        verbose_name = "Podcast scraping configuration"
        verbose_name_plural = "Podcast scraping configurations"

    def get_public_url_pcast(self):
        return 'pcast://' + os.environ['AWS_BUCKET'] + '/' + self.get_path()

    def get_public_url(self):
        return 'http://' + os.environ['AWS_BUCKET'] + '/' + self.get_path()

    def get_path(self):
        return self.slug + '.xml'

    def __str__(self):
        return self.slug


class Podcast(models.Model):
    config = models.OneToOneField('PodcastScrapingConfiguration', related_name='podcast')

    # RSS fields
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    link = models.URLField(unique=True)
    language = models.CharField(max_length=10)
    image_url = models.URLField()

    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"

    def generate_rss_xml(self):
        rss = ET.Element('rss')
        channel = ET.SubElement(rss, 'channel')

        ET.SubElement(channel, 'docs').text = 'http://blogs.law.harvard.edu/tech/'
        ET.SubElement(channel, 'title').text = self.title
        ET.SubElement(channel, 'language').text = self.language
        ET.SubElement(channel, 'link').text = self.link
        ET.SubElement(channel, 'description').text = self.description
        ET.SubElement(channel, '{%s}image' % ITUNES_NS, href=self.image_url)
        ET.SubElement(channel, 'pubDate').text = formatdate()

        for podcast_item in self.items.all():
            channel.append(podcast_item.generate_rss_item_xml())

        return rss

    def generate_rss(self):
        return ET.tostring(self.generate_rss_xml())

    def publish_to_aws(self, transfer_client=None):
        if transfer_client is None:
            transfer_client = s3_transfer_client()
        with temp_file() as file_path:
            with open(file_path, 'wb') as f:
                f.write(self.generate_rss())
            public_url = self.config.get_path()
            transfer_client.upload_file(
                file_path, os.environ['AWS_BUCKET'],
                public_url,
                extra_args={'ACL': 'public-read', 'ContentType': 'application/xml'}
            )
        return public_url

    def __str__(self):
        return self.title


class PodcastItemManager(models.Manager):
    def create(self, *args, **kwargs):
        with urllib.request.urlopen(kwargs['audio_url']) as url:
            meta = url.info()
            kwargs['audio_length'] = int(meta.get('Content-Length'))
            if not kwargs.get('pub_date'):
                parsed = parsedate(meta['Last-Modified'])
                kwargs['pub_date'] = datetime.datetime(*parsed[:6])
        kwargs['audio_type'] = 'audio/mpeg'
        super(PodcastItemManager, self).create(*args, **kwargs)


class PodcastItem(models.Model):
    objects = PodcastItemManager()

    podcast = models.ForeignKey('Podcast', related_name='items')

    # RSS Fields
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    link = models.URLField()
    audio_url = models.URLField()
    audio_length = models.PositiveIntegerField()
    AUDIO_TYPE_CHOICES = (
        ('audio/mpeg', 'audio/mpeg'),
    )
    audio_type = models.CharField(max_length=15, choices=AUDIO_TYPE_CHOICES)
    audio_duration = models.DurationField(null=True, blank=True)
    pub_date = models.DateTimeField()

    class Meta:
        unique_together = (("podcast", "link"),)
        ordering = ('-pub_date', 'pk', )
        verbose_name = "Podcast item"
        verbose_name_plural = "Podcast items"

    def generate_rss_item_xml(self):
        item = ET.Element('item')

        ET.SubElement(item, 'title').text = self.title
        ET.SubElement(item, 'link').text = self.link
        ET.SubElement(item, 'guid').text = self.audio_url
        ET.SubElement(item, 'description').text = self.description
        ET.SubElement(item, 'enclosure',
                      url=self.audio_url,
                      length=str(self.audio_length),
                      type=self.audio_type)
        ET.SubElement(item, '{%s}duration' % ITUNES_NS).text = str(self.audio_duration)
        pub_date_timestamp = time.mktime(self.pub_date.timetuple())
        ET.SubElement(item, 'pubDate').text = formatdate(pub_date_timestamp)
        return item

    def __str__(self):
        return self.title


class PodcastIgnoreItem(models.Model):
    podcast = models.ForeignKey('Podcast', related_name='ignore_items')
    link = models.URLField()

    class Meta:
        unique_together = (("podcast", "link"),)
        verbose_name = "Podcast ignore item"
        verbose_name_plural = "Podcast ignore items"

    def __str__(self):
        return self.link
