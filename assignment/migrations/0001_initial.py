# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('due_date', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('link', models.CharField(max_length=200, null=True, blank=True)),
                ('content', models.TextField(max_length=15000)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.CharField(max_length=10, null=True, blank=True)),
                ('details', models.CharField(default=None, max_length=1000, null=True, blank=True)),
                ('assigned', models.ForeignKey(to='student.Student')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewConvo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=10000, null=True, blank=True)),
                ('score', models.CharField(max_length=10, null=True, blank=True)),
                ('details', models.CharField(default=None, max_length=1000, null=True, blank=True)),
                ('review', models.ForeignKey(to='assignment.Review')),
                ('student', models.ForeignKey(to='student.Student')),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('files', models.CharField(max_length=15000)),
                ('assignment', models.ForeignKey(to='assignment.Assignment')),
                ('student', models.ForeignKey(to='student.Student')),
            ],
        ),
        migrations.AddField(
            model_name='review',
            name='submission',
            field=models.ForeignKey(to='assignment.Submission'),
        ),
        migrations.AddField(
            model_name='permission',
            name='review',
            field=models.ManyToManyField(to='assignment.Review'),
        ),
        migrations.AddField(
            model_name='permission',
            name='student',
            field=models.ForeignKey(to='student.Student'),
        ),
    ]
