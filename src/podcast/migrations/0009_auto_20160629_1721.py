# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-29 17:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0008_podcastitem_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='link',
            field=models.URLField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='podcastitem',
            unique_together=set([('podcast', 'link')]),
        ),
    ]
