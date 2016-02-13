# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='enable_codework',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment',
            name='enable_peer_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment',
            name='enable_stats',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment',
            name='enable_submission',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='submission',
            name='files',
            field=models.CharField(max_length=15000, null=True, blank=True),
        ),
    ]
