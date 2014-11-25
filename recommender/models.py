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
    review_score = models.CharField(max_length=10)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'review_userid', 'review_score',)
    list_filter = ('userid', 'review_userid')

class ReviewText(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    userid = models.CharField(max_length=50)
    review_pk = models.IntegerField(max_length=10)
    review_text =  models.CharField(max_length=10000, null=True)

class ReviewTextAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'userid', 'review_pk', 'review_text')
    search_fields = ('review_text',)
    list_filter = ('review_pk',)

class PredictionForm(forms.Form):
    test_data = forms.CharField(widget=forms.Textarea)
    fields = ('test_data')

class ReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea)
    field = ('review_text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('review_score')

class ReportForm(forms.Form):
    report_link = forms.CharField(max_length=100)
    fields = ('report_link')
