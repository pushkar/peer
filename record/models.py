from django.db import models
from django import forms
from django.contrib import admin, messages
from django.forms.widgets import RadioSelect
from student.models import *

class Record(models.Model):
    student = models.ForeignKey(Student)
    details = models.CharField(max_length=2000)

    def __unicode__(self):
        return unicode(self.student)

## Add their final objective in life, things they want to achieve!

class TopicGroup(models.Model):
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

class Topic(models.Model):
    order = models.IntegerField()
    group = models.ForeignKey(TopicGroup)
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['order']
