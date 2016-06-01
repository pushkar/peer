from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from assignment.models import *

class IOSource(models.Model):
    ''' Contains source url for grabbing Input/Output pairs for each Assignment '''
    assignment = models.ForeignKey(Assignment)
    url = models.CharField(max_length=200)

class IOPair(models.Model):
    ''' Contains Input/Output pairs for each Assignment '''
    assignment = models.ForeignKey(Assignment)
    input = models.CharField(max_length=550000)
    output = models.CharField(max_length=100000)

    def __unicode__(self):
        return unicode(self.input + " -> " + self.output)

    def input_av(self):
        if not self.input:
            return "-"
        ret = str(self.input)
        ret_len = len(ret)
        ret = ret[:30]
        if ret_len > 30:
            ret += "..."
        return ret

    def output_av(self):
        if not self.output:
            return "-"
        ret = str(self.output)
        ret_len = len(ret)
        ret = ret[:30]
        if ret_len > 30:
            ret += "..."
        return ret

class IOSolution(models.Model):
    ''' Contains Input/Output pairs submited by students '''
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    pair = models.ForeignKey(IOPair)
    output_submitted = models.CharField(max_length=100000, null=True, blank=True)
    score = models.CharField(max_length=10, default="0.0")
    comments = models.CharField(max_length=2000, null=True, blank=True)

    def pair_av(self):
        return self.pair.input[:10]

    def output_submitted_av(self):
        if not self.output_submitted:
            return "-"
        ret = str(self.output_submitted)
        ret_len = len(ret)
        ret = ret[:30]
        if ret_len > 30:
            ret += "..."
        return ret

    def is_late(self):
        if self.updated > self.assignment.due_date:
            return True
        else:
            return False

    def late_av(self):
        if self.is_late():
            return "Late"
        else:
            return ""

class IOSubmission(models.Model):
    ''' Contains Scores for Assignments
        Deprecated - To be Removed
    '''
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    score = models.CharField(max_length=10)
    comments = models.CharField(max_length=2000, null=True, blank=True)

class IOSourceAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'url')

class IOPairAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'input_av', 'output_av')
    list_filter = ('assignment__name', )

class IOSolutionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'created', 'updated', 'late_av', 'output_submitted_av', 'score')
    search_fields = ('student__lastname', 'student__firstname', 'student__username')
    list_filter = ('assignment__name', )

class IOSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score')
    list_filter = ('assignment__name',)
