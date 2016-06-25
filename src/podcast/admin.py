from django.contrib import admin
from .models import Podcast
from .models import PodcastItem
from .models import PodcastScrapingSteps
from .models import PodcastScrapingConfiguration

from django.contrib.postgres.fields import JSONField
from jsoneditor.forms import JSONEditor


class PodcastScrapingConfigurationInline(admin.TabularInline):
    readonly_fields = ['podcast']
    model = PodcastScrapingConfiguration


@admin.register(PodcastScrapingSteps)
class PodcastScrapingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
    inlines = [PodcastScrapingConfigurationInline]


class PodcastItemInline(admin.TabularInline):
    model = PodcastItem
    readonly_fields = [f.name for f in PodcastItem._meta.get_fields()]


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Podcast._meta.get_fields()]
    inlines = [PodcastItemInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
