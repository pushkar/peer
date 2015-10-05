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


class Topic(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000)

    class Meta:
        ordering = ['order']

class RecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'details')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'details')
