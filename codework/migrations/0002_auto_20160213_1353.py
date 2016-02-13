# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iopair',
            name='input',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='iopair',
            name='output',
            field=models.CharField(max_length=50000),
        ),
        migrations.AlterField(
            model_name='iosolution',
            name='output_submitted',
            field=models.CharField(max_length=50000, null=True, blank=True),
        ),
    ]
