# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-18 18:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='destination_slug',
        ),
        migrations.AddField(
            model_name='podcastscraping',
            name='destination_slug',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='podcastscraping',
            name='podcast',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='podcast.Podcast'),
        ),
    ]
