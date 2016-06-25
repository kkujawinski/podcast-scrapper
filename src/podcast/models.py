from django.db import models
from django.contrib.postgres.fields import JSONField

from xml.etree import ElementTree as ET
from email.utils import formatdate


ITUNES_NS = '{http://www.itunes.com/dtds/podcast-1.0.dtd}image'
ET.register_namespace('itunes', ITUNES_NS)


class PodcastScrapingSteps(models.Model):
    name = models.CharField(max_length=50)
    steps = JSONField()
    # [stepConfiguration1, stepConfiguration2]

    class Meta:
        verbose_name = "Podcast scraping steps"
        verbose_name_plural = "Podcast scraping steps"

    def scrap(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'PodcastScrapingSteps<%s>' % str(self)


class PodcastScrapingConfiguration(models.Model):
    steps = models.ForeignKey('PodcastScrapingSteps')
    podcast = models.ForeignKey('Podcast', null=True, blank=True)

    slug = models.CharField(max_length=50, unique=True)
    start_url = models.URLField()

    class Meta:
        verbose_name = "Podcast scraping configuration"
        verbose_name_plural = "Podcast scraping configurations"

    def __str__(self):
        return self.slug


class Podcast(models.Model):
    # RSS fields
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    link = models.URLField()
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

        for podcast_item in self.items:
            channel.append(podcast_item.generate_rss_item_xml())

        return rss

    def generate_rss(self):
        return ET.tostring(self.generate_rss_xml())

    def __str__(self):
        pass


class PodcastItem(models.Model):
    podcast = models.ForeignKey('Podcast', related_name='items')

    # RSS Fields
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    link = models.URLField()
    audio_url = models.URLField()
    audio_length = models.PositiveIntegerField()
    AUDIO_TYPE_CHOICES = (
        ('audio/mpeg', 'audio/mpeg'),
    )
    audio_type = models.CharField(max_length=15, choices=AUDIO_TYPE_CHOICES)
    audio_duration = models.DurationField()

    class Meta:
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
                      length=self.audio_length,
                      type=self.audio_type)
        ET.SubElement(item, '{%s}duration' % ITUNES_NS).text = self.duration
        return item

    # def __str__(self):
    #     pass


# StepConfiguration
# - {xpath: '//'},
# - {xpath: '//', action=store, name=audio_url} - no transition
# - {xpath: '//', action=follow},
# - {xpath: '//', action=parse_json},
# - {jsonpath: '//'}
