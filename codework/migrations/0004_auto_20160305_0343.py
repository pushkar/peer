# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codework', '0003_auto_20160222_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iopair',
            name='input',
            field=models.CharField(max_length=50000),
        ),
    ]
