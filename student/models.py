from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

USER_TYPES = (
    ('student', 'Student'),
    ('ta', 'TA'),
    ('superta', 'Admin'),
)

class Student(models.Model):
    username = models.CharField(max_length=50)
    usertype = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.CharField(max_length=50)
    email_tsq = models.CharField(max_length=50, null=True)
    gtid = models.CharField(max_length=12)
    lastname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    optin = models.BooleanField(default=False)

    class Meta(object):
        ordering = ['lastname']

    def __str__(self):
        return str(self.lastname + ", " + self.firstname + " (" + self.username + ")")

class StudentLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student)
    details = models.CharField(default=None, max_length=1000)

    class Meta:
        ordering = ['created']

class StudentNotes(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    notes = models.CharField(default=None, max_length=2000)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return "%s..." % self.notes[50:]

class Banish(models.Model):
    ''' Contains the number of times a student accesses something
    '''
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    ip = models.CharField(max_length=20, default="")
    count = models.CharField(max_length=10, default="1")
    violations = models.CharField(max_length=10, default="0")

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    gtid = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '987654321'}))
    fields = ('username', 'gtid')

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    fields = ('username')
