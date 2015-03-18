from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect
from student.models import *

class Score(models.Model):
    student = models.ForeignKey(Student)
    value = models.FloatField(default=None, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.student)

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'value')
    search_fields = ('student__username', 'student__firstname', 'student__lastname')


class PredictionForm(forms.Form):
    test_data = forms.CharField(widget=forms.Textarea)
    fields = ('test_data')
