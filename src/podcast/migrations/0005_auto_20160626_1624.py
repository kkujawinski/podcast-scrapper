# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 16:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0004_remove_podcastscrapingsteps_podcast'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podcastitem',
            old_name='duration',
            new_name='audio_duration',
        ),
    ]