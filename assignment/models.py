from django.db import models
from django import forms
from django.contrib import admin, messages
from django.forms.widgets import RadioSelect
from student.models import *

import csv
import random
import urllib2

class Assignment(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return unicode(self.name)

class AssignmentPage(models.Model):
    assignment = models.ForeignKey(Assignment)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(max_length=15000)

    class Meta:
        ordering = ['pk']

class Submission(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    files = models.CharField(max_length=15000)

    def __unicode__(self):
        return unicode(unicode(self.student) + ", " + unicode(self.assignment))

# Each Review is assigned to someone and has a score
class Review(models.Model):
    submission = models.ForeignKey(Submission)
    assigned = models.ForeignKey(Student)
    score = models.CharField(max_length=10, null=True, blank=True)
    details = models.CharField(default=None, max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return unicode(unicode(self.submission.student) + " - R" + unicode(self.pk) + ", " + unicode(self.submission.assignment))

# Who can access the review other than the one who it was assigned to?
class Permission(models.Model):
    student = models.ForeignKey(Student)
    review = models.ManyToManyField(Review)

    def __unicode__(self):
        return unicode(unicode(self.student) + " Permissions ")

class ReviewConvo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review)
    student = models.ForeignKey(Student)
    text =  models.CharField(max_length=10000, null=True, blank=True)
    score = models.CharField(max_length=10, null=True, blank=True)
    details = models.CharField(default=None, max_length=1000, null=True, blank=True)

    class Meta:
        ordering = ['created']
        get_latest_by = ['created']


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date')

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'student', 'assignment', 'files')
    search_fields = ('student__lastname', 'student__firstname', 'student__username')
    list_filter = ('assignment__name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'submission', 'assigned', 'score')
    search_fields = ('submission__student__lastname', 'submission__student__firstname', 'submission__student__username', 'submission__student__group_id')
    list_filter = ('submission__assignment__name', 'assigned__usertype', )


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'student',)
    list_filter = ('review',)
    filter_horizontal = ('review',)


class ReviewConvoAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'text')
    search_fields = ('student__username', 'student__firstname', 'student__lastname', 'review__submission__student__username',
                'review__submission__student__firstname', 'review__submission__student__lastname')
    list_filter = ('review',)


# Form Views
class ReviewConvoForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'style': 'width:90%'}))
    field = ('text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('score')

class ReportForm(forms.Form):
    file_name = forms.CharField(max_length=100)
    file_link = forms.CharField(max_length=1000)
    fields = ('file_name', 'file_link')
