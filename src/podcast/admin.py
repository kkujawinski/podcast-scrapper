from django.contrib import admin
from urllib.parse import urljoin
from .models import Podcast
from .models import PodcastItem
from .models import PodcastIgnoreItem
from .models import PodcastScrapingSteps
from .models import PodcastScrapingConfiguration

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
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    inlines = [PodcastScrapingConfigurationInline]


class PodcastItemInline(admin.TabularInline):
    model = PodcastItem
    fields = ['title', 'show_link', 'description', 'pub_date']
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def show_link(sel, obj):
        full_link = urljoin(obj.podcast.link, obj.link)
        return '<a href="{0}">{1}</a>'.format(full_link, obj.link)
    show_link.short_description = 'Link'
    show_link.allow_tags = True


class PodcastIgnoreItemInline(admin.TabularInline):
    model = PodcastIgnoreItem
    fields = ['show_link']
    readonly_fields = fields

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


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'language', 'show_link', 'show_image',
              'last_scrap', 'show_config']
    readonly_fields = fields
    inlines = [PodcastItemInline, PodcastIgnoreItemInline]
    actions = [publish_to_aws]

    def show_link(sel, obj):
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

    def last_scrap(sel, obj):
        return obj.config.last_scrap

    def has_add_permission(self, request, obj=None):
        return False
