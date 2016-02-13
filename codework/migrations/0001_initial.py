# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '__first__'),
        ('assignment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IOPair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('input', models.CharField(max_length=500)),
                ('output', models.CharField(max_length=2000)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
            ],
        ),
        migrations.CreateModel(
            name='IOSolution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('output_submitted', models.CharField(max_length=2000, null=True, blank=True)),
                ('comments', models.CharField(max_length=2000, null=True, blank=True)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
                ('pair', models.ForeignKey(to='codework.IOPair')),
                ('student', models.ForeignKey(to='student.Student')),
            ],
        ),
        migrations.CreateModel(
            name='IOSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=200)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
            ],
        ),
        migrations.CreateModel(
            name='IOSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.CharField(max_length=10)),
                ('comments', models.CharField(max_length=2000, null=True, blank=True)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
                ('student', models.ForeignKey(to='student.Student')),
            ],
        ),
    ]
