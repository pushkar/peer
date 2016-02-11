from __future__ import unicode_literals

from django.db import models
from assignment.models import *

class IOSource(models.Model):
    assignment = models.ForeignKey(Assignment)
    url = models.CharField(max_length=200)

class IOPair(models.Model):
    assignment = models.ForeignKey(Assignment)
    input = models.CharField(max_length=1000)
    output = models.CharField(max_length=50000)

    def __unicode__(self):
        return unicode(self.input + " -> " + self.output)

class IOSolution(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    pair = models.ForeignKey(IOPair)
    output_submitted = models.CharField(max_length=50000, null=True, blank=True)
    comments = models.CharField(max_length=2000, null=True, blank=True)

class IOSubmission(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    score = models.CharField(max_length=10)
    comments = models.CharField(max_length=2000, null=True, blank=True)

class IOSourceAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'url')

class IOPairAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'input', 'output')

class IOSolutionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'pair', 'output_submitted')
    search_fields = ('stduent__lastname', 'student__firstname', 'student__username')
    list_filter = ('assignment__name',)

class IOSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score')
    list_filter = ('assignment__name',)
