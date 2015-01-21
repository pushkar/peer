from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class StudentInfo(models.Model):
    userid = models.CharField(max_length=50)
    score = models.FloatField()

    def __unicode__(self):
        return self.userid

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'score')
    search_fields = ('userid',)


class PredictionForm(forms.Form):
    test_data = forms.CharField(widget=forms.Textarea)
    fields = ('test_data')
