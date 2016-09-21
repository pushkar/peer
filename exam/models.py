from django.db import models
from django import forms
from django.contrib import admin, messages
from django.forms.widgets import RadioSelect
from student.models import *

class Exam(models.Model):
    short_name = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

class StudentInfo(models.Model):
    student = models.ForeignKey(Student)
    proficiency = models.CharField(max_length=10, default="0.0")

    def __unicode__(self):
        return unicode(self.student)

class Question(models.Model):
    exam = models.ForeignKey(Exam)
    text = models.CharField(max_length=1000)
    hardness = models.CharField(max_length=10, default="0.0")
    details = models.CharField(max_length=200, blank=True, null=True)
    strategy = models.CharField(max_length=200, default="random")

    def __unicode__(self):
        return unicode(self.text)

class Answer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student)
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=10)
    text = models.CharField(max_length=1000)
    correctness = models.CharField(max_length=10, default="0.5")
    details = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.text)

class TempExam(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    exam = models.ForeignKey(Exam)
    finished = models.CharField(max_length=100, blank=True, null=True)
    student = models.ForeignKey(Student)
    details = models.CharField(max_length=50000, blank=True, null=True)
