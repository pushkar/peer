# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0004_auto_20160305_0343'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosolution',
            name='score',
            field=models.CharField(default='0.0', max_length=10),
        ),
    ]
