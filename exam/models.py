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

    def __str__(self):
        return str(self.name)

class StudentInfo(models.Model):
    student = models.ForeignKey(Student)
    proficiency = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.student)

class Strategy(models.Model):
    name = models.CharField(max_length=100)
    params = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.name)

class Question(models.Model):
    exam = models.ForeignKey(Exam)
    text = models.CharField(max_length=1000)
    hardness = models.CharField(max_length=10, blank=True, null=True)
    details = models.CharField(max_length=10000, blank=True, null=True)
    strategy = models.ForeignKey(Strategy)

    def __str__(self):
        return str(self.text)

class Answer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student)
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=10)
    text = models.CharField(max_length=1000)
    correctness = models.CharField(max_length=200, blank=True, null=True)
    finished = models.BooleanField(default=False)
    feedback = models.CharField(max_length=1000, blank=True, null=True)
    details = models.CharField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return str(self.text)

class MC(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.CharField(Student, max_length=100)
    question = models.ForeignKey(Exam)
    answers = models.ManyToManyField(Answer)
    finished = models.BooleanField(default=False)
    details = models.CharField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return str(self.answers)

class Grading(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.CharField(Student, max_length=100)
    mc = models.ForeignKey(MC)
    grade = models.CharField(max_length=100, blank=True, null=True)

class TempExam(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    exam = models.ForeignKey(Exam)
    finished = models.BooleanField(default=False)
    details = models.CharField(max_length=50000, blank=True, null=True)
