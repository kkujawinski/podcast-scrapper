# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-14 21:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0020_mp3_based_pub_date_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcastignoreitem',
            name='ignore_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 8, 14, 21, 10, 35, 665079, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
