# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0007_auto_20160313_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iosolution',
            name='output_submitted',
            field=models.CharField(max_length=100000, null=True, blank=True),
        ),
    ]
