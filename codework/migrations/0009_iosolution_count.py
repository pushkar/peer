# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-25 00:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0008_auto_20160531_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosolution',
            name='count',
            field=models.CharField(default='0', max_length=10),
        ),
    ]
