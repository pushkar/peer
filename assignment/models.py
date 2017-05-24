from django.db import models
from django import forms
from django.contrib import admin, messages
from student.models import Student

class Assignment(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    enable_submission = models.BooleanField(default=False)
    enable_codework = models.BooleanField(default=False)
    enable_peer_review = models.BooleanField(default=False)
    enable_stats = models.BooleanField(default=False)

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
