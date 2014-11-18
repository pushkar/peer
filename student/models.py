from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class Student(models.Model):
    userid = models.CharField(max_length=50)
    usertype = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    gtid = models.CharField(max_length=12)
    lastname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)

    def __unicode__(self):
        return self.userid

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'gtid', 'firstname', 'lastname', 'email')
    search_fields = ('userid', 'firstname', 'lastname')
    list_filter = ('usertype',)


class LoginForm(forms.Form):
    userid = forms.CharField(initial='pkolhe3')
    gtid = forms.CharField(initial='9022*****')
    fields = ('userid', 'gtid')
