from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class StudentInfo(models.Model):
    userid = models.CharField(max_length=50)
    score = models.CharField(max_length=10)
    report = models.CharField(max_length=50, null=True)

    def __unicode__(self):
        return self.userid

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'score', 'report')
    search_fields = ('userid',)

class Review(models.Model):
    userid = models.CharField(max_length=50)
    review_userid = models.CharField(max_length=50)
    text = models.CharField(max_length=5000, null=True)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'review_userid', 'text',)
    search_fields = ('text',)
    list_filter = ('userid', 'review_userid')


class PredictionForm(forms.Form):
    test_data = forms.CharField(widget=forms.Textarea)
    fields = ('test_data')

class ReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea)
    field = ('review_text')

class ReportForm(forms.Form):
    report_link = forms.CharField(max_length=100)
    fields = ('report_link')
