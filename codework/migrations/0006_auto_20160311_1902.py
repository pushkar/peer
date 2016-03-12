# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0005_iosolution_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iopair',
            name='input',
            field=models.CharField(max_length=550000),
        ),
    ]
