from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class StudentInfo(models.Model):
    userid = models.CharField(max_length=50)

    def __unicode__(self):
        return self.userid

class Assignment(models.Model):
    assignment_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True)

class AssignmentPage(models.Model):
    assignment_name = models.CharField(max_length=50)
    page_name = models.CharField(max_length=200)
    page_title = models.CharField(max_length=200)
    page_content = models.TextField(max_length=5000)

class Submission(models.Model):
    user_pk = models.IntegerField(max_length=50)
    assignment_name = models.CharField(max_length=100)
    score = models.CharField(max_length=10)
    report = models.CharField(max_length=200, null=True)

class Review(models.Model):
    submission_pk = models.IntegerField(max_length=50)
    review_userid = models.CharField(max_length=50)
    review_score = models.CharField(max_length=10)

class ReviewText(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    userid = models.CharField(max_length=50)
    review_pk = models.IntegerField(max_length=10)
    review_text =  models.CharField(max_length=10000, null=True)


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment_name', 'name', 'due_date')

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment_name', 'page_name', 'page_title')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_pk', 'assignment_name', 'report', 'score')

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid')
    search_fields = ('userid',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission_pk', 'review_userid', 'review_score',)

class ReviewTextAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'userid', 'review_pk', 'review_text')
    search_fields = ('review_text',)
    list_filter = ('review_pk',)


# Form Views
class ReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea)
    field = ('review_text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('review_score')

class ReportForm(forms.Form):
    report_link = forms.CharField(max_length=100)
    fields = ('report_link')
