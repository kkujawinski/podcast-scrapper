# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 16:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0005_auto_20160626_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcastscrapingconfiguration',
            name='podcast',
        ),
        migrations.AddField(
            model_name='podcast',
            name='config',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='podcast', to='podcast.PodcastScrapingConfiguration'),
            preserve_default=False,
        ),
    ]