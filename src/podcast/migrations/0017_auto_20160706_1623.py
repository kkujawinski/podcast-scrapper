# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-06 16:23
from __future__ import unicode_literals

from django.db import migrations
import podcast.models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0016_auto_20160706_0456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='description',
            field=podcast.models.TruncatingCharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='title',
            field=podcast.models.TruncatingCharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='podcastitem',
            name='description',
            field=podcast.models.TruncatingCharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='podcastitem',
            name='title',
            field=podcast.models.TruncatingCharField(max_length=200),
        ),
    ]