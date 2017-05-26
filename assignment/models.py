from django.db import models
from django import forms
from django.contrib import admin
from django.contrib import messages
from student.models import Student

class Assignment(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    released = models.BooleanField(default=False)
    enable_codework = models.BooleanField(default=False)
    num_codeproblems = models.PositiveIntegerField(default=10)
    url = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)

    class Meta(object):
        ordering = ['due_date']

class AssignmentPage(models.Model):
    assignment = models.ForeignKey(Assignment)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(max_length=15000)

    class Meta(object):
        ordering = ['pk']

    def __str__(self):
        return "%s's page: %s" % (self.assignment, self.name)

class IOPair(models.Model):
    ''' Contains Input/Output pairs for each Assignment '''
    assignment = models.ForeignKey(Assignment)
    input = models.CharField(max_length=550000)
    output = models.CharField(max_length=100000)

    def __str__(self):
        return str(self.input_av() + " -> " + self.output_av())

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
    count = models.PositiveIntegerField(default=0)
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    pair = models.ForeignKey(IOPair)
    output_submitted = models.CharField(max_length=100000, null=True, blank=True)
    score = models.FloatField(default=0.0)
    comments = models.CharField(max_length=2000, null=True, blank=True)

    class Meta(object):
        ordering = ['pk']

    def __str__(self):
        return str(self.pair_av() + " -> " + self.output_submitted_av())

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
