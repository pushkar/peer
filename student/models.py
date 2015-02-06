from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class Student(models.Model):
    username = models.CharField(max_length=50)
    usertype = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    gtid = models.CharField(max_length=12)
    lastname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    group_id = models.IntegerField()

    def __unicode__(self):
        return unicode(self.lastname + ", " + self.firstname + " (" + self.username + ")")

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'gtid', 'firstname', 'lastname', 'email', 'usertype')
    search_fields = ('username', 'gtid', 'firstname', 'lastname')
    list_filter = ('group_id', )


class LoginForm(forms.Form):
    username = forms.CharField(initial='pkolhe3')
    gtid = forms.CharField(initial='9022*****')
    fields = ('username', 'gtid')
