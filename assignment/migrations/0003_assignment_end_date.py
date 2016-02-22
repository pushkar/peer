# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0002_auto_20160213_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
    ]
