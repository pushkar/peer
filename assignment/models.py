from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect
from student.models import *

import csv

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
    content = models.TextField(max_length=5000)

class Submission(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    report = models.CharField(max_length=1000, null=True)

    def __unicode__(self):
        return unicode(self.student)

class Review(models.Model):
    submission = models.ForeignKey(Submission)
    score = models.CharField(max_length=10)

    def __unicode__(self):
        return unicode("Review for " + unicode(self.submission.student))

class Permission(models.Model):
    review = models.ForeignKey(Review)
    student = models.ForeignKey(Student)

class ReviewConvo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review)
    student = models.ForeignKey(Student)
    text =  models.CharField(max_length=10000, null=True)
    score = models.CharField(max_length=10, null=True, blank=True)


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date')
    actions = ['populate_submissions']

    def populate_submissions(self, request, queryset):
        added_count = 0
        notadded_count = 0

        for a in queryset:
            with open('submissions.csv', 'rb') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    s = Student.objects.get(username=row[0])
                    if s:
                        Submission.objects.get_or_create(student=s, assignment=a, report=row[1])
                        added_count = added_count + 1
                    else:
                        notadded_count = notadded_count + 1
        self.message_user(request, "%s student submissions were added. %s files were skipped." % (str(added_count), str(notadded_count))) 
    populate_submissions.short_description = "Populate with Submissions"

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'report')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'score')

class PermissionAdmin(admin.ModelAdmin):
    list_display = ('review', 'student')
    list_filter = ('review__submission__student__username',)
    #filter_horizontal = ('student',)


class ReviewConvoAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'text')
    search_fields = ('text',)


# Form Views
class ReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea)
    field = ('text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('score')

class ReportForm(forms.Form):
    report_link = forms.CharField(max_length=100)
    fields = ('link')
