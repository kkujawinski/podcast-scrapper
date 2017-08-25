import subprocess

from django.contrib import admin
from django.contrib import messages
from urllib.parse import urljoin
from .models import Podcast
from .models import PodcastItem
from .models import PodcastIgnoreItem
from .models import PodcastScrapingSteps
from .models import PodcastScrapingConfiguration
from .models import PodcastSuggestion

from django.core import urlresolvers
from django.contrib.postgres.fields import JSONField
from jsoneditor.forms import JSONEditor


class PodcastScrapingConfigurationInline(admin.TabularInline):
    model = PodcastScrapingConfiguration
    readonly_fields = ['last_scrap', 'show_podcast']

    def show_podcast(sel, obj):
        if obj.podcast:
            link = urlresolvers.reverse('admin:podcast_podcast_change', args=(obj.podcast.id,))
            return '<a href="{}">Show podcast</a>'.format(link)
    show_podcast.short_description = 'Podcast'
    show_podcast.allow_tags = True


@admin.register(PodcastScrapingSteps)
class PodcastScrapingAdmin(admin.ModelAdmin):
    fields = ['name', 'steps']
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    inlines = [PodcastScrapingConfigurationInline]


class PodcastItemInline(admin.TabularInline):
    model = PodcastItem
    fields = ['title', 'show_links', 'description', 'pub_date']
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def show_links(sel, obj):
        full_link = urljoin(obj.podcast.link, obj.link)
        return ''.join((
            'URL: <a href="{0}">{1}</a>'.format(full_link, obj.link),
            '<br/><br/>',
            'AUDIO: <a href="{0}">{0}</a>'.format(obj.audio_url),
        ))
    show_links.short_description = 'Links'
    show_links.allow_tags = True


class PodcastIgnoreItemInline(admin.TabularInline):
    model = PodcastIgnoreItem
    fields = ['show_link', 'ignore_date']
    readonly_fields = fields
    ordering = ("-ignore_date", "-id",)

    def has_add_permission(self, request, obj=None):
        return False

    def show_link(sel, obj):
        full_link = urljoin(obj.podcast.link, obj.link)
        return '<a href="{0}">{1}</a>'.format(full_link, obj.link)
    show_link.short_description = 'Link'
    show_link.allow_tags = True


def publish_to_aws(modeladmin, request, queryset):
    for podcast in queryset:
        podcast.publish_to_aws()
    PodcastScrapingConfiguration.objects.publish_index_to_aws()
publish_to_aws.short_description = "Publish RSS"


def scrap(modeladmin, request, queryset):
    for podcast in queryset:
        slug = podcast.config.slug
        try:
            output = subprocess.check_output(['django-admin', 'scrap',
                                              '--podcast', slug])
        except subprocess.CalledProcessError as e:
            messages.error(request, str(e))
        else:
            messages.info(request, 'Scrapping for %s is done' % slug)
scrap.short_description = "Scrap"


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'description', 'language', 'show_link', 'show_image',
              'last_scrap', 'show_config', 'show_history']
    readonly_fields = fields
    inlines = [PodcastItemInline, PodcastIgnoreItemInline]
    actions = [publish_to_aws, scrap]

    def slug(self, obj):
        return obj.config.slug

    def show_link(self, obj):
        return '<a href="{0}">{0}</a>'.format(obj.link)
    show_link.short_description = 'Link'
    show_link.allow_tags = True

    def show_config(sel, obj):
        link = urlresolvers.reverse('admin:podcast_podcastscrapingsteps_change', args=(obj.config.steps.id,))
        return '<a href="{}">Show configuration</a>'.format(link)
    show_config.short_description = 'Config'
    show_config.allow_tags = True

    def show_image(sel, obj):
        return '<img src="{0}" style="max-width: 40%;"/>'.format(obj.image_url)
    show_image.short_description = 'Image'
    show_image.allow_tags = True

    def show_history(self, obj):
        url = obj.get_history_chart_url()
        return '<img src="{0}" style="max-width: 40%;"/>'.format(url)
    show_history.short_description = 'History'
    show_history.allow_tags = True


    def last_scrap(sel, obj):
        return obj.config.last_scrap

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PodcastSuggestion)
class PodcastSuggestionAdmin(admin.ModelAdmin):
    fields = ['show_url', 'email']
    readonly_fields = fields

    def show_url(sel, obj):
        return '<a href="{0}">{0}</a>'.format(obj.url)
    show_url.short_description = 'Link'
    show_url.allow_tags = True
