from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class Global(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=1000)

    def __unicode__(self):
        return unicode(self.key)

class GlobalAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'value')
    search_fields = ('key', )

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

    actions = ['optin_program']

    def optin_program(self, request, queryset):
        opt_count = 0
        for s in queryset:
            opt = OptIn.objects.get_or_create(student=s, value=False)
            if opt[1]:
                opt_count += 1

        self.message_user(request, "%d of %d students were put in the Opt In program." % (opt_count, len(queryset)) )

    optin_program.short_description = "Put in the Opt In program"

class OptIn(models.Model):
    student = models.ForeignKey(Student)
    value = models.BooleanField(default=False)

class OptInAdmin(admin.ModelAdmin):
    list_display = ('student', 'value')

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    gtid = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '987654321'}))
    fields = ('username', 'gtid')

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    fields = ('username')
