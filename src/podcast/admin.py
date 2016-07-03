from django.contrib import admin
from .models import Podcast
from .models import PodcastItem
from .models import PodcastIgnoreItem
from .models import PodcastScrapingSteps
from .models import PodcastScrapingConfiguration

from django.contrib.postgres.fields import JSONField
from jsoneditor.forms import JSONEditor


class PodcastScrapingConfigurationInline(admin.TabularInline):
    model = PodcastScrapingConfiguration


@admin.register(PodcastScrapingSteps)
class PodcastScrapingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    inlines = [PodcastScrapingConfigurationInline]


class PodcastItemInline(admin.TabularInline):
    model = PodcastItem
    readonly_fields = [f.name for f in PodcastItem._meta.local_fields]

    def has_add_permission(self, request, obj=None):
        return False


class PodcastIgnoreItemInline(admin.TabularInline):
    model = PodcastIgnoreItem
    readonly_fields = [f.name for f in PodcastIgnoreItem._meta.local_fields]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Podcast._meta.local_fields]
    inlines = [PodcastItemInline, PodcastIgnoreItemInline]

    def has_add_permission(self, request, obj=None):
        return False
