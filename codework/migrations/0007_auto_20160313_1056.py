# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0006_auto_20160311_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iopair',
            name='output',
            field=models.CharField(max_length=100000),
        ),
    ]
