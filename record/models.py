from django.db import models
from django import forms
from django.contrib import admin, messages
from django.forms.widgets import RadioSelect
from student.models import *

class StudentDetails(models.Model):
    student = models.ForeignKey(Student)
    profession = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    objectives = models.CharField(max_length=100, blank=True, null=True)
    details = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.student)

class Objectives(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)

class Record(models.Model):
    student = models.ForeignKey(Student, related_name='student')
    assigned = models.ForeignKey(Student, related_name='assigned')
    locked = models.CharField(max_length=10, default="0")
    details = models.CharField(max_length=2000)

    def __str__(self):
        return str(self.student)

class TopicGroup(models.Model):
    key = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Topic(models.Model):
    order = models.IntegerField()
    group = models.ForeignKey(TopicGroup, related_name='group')
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta(object):
        ordering = ['order']
