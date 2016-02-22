# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import pytz


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0002_auto_20160213_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosolution',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 15, 0, 0, tzinfo=pytz.timezone('US/Eastern')), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iosolution',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 15, 0, 0, tzinfo=pytz.timezone('US/Eastern')), auto_now=True),
            preserve_default=False,
        ),
    ]
