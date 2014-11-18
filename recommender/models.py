from django.db import models
from django import forms
from django.forms.widgets import RadioSelect

class Student(models.Model):
    userid = models.CharField(max_length=50)
    score = models.CharField(max_length=10)
    report = models.CharField(max_length=50)

    def __unicode__(self):
        return self.userid

class Review(models.Model):
    userid = models.CharField(max_length=50)
    review = models.CharField(max_length=5000)
