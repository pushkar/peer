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

    class Meta:
        ordering = ['lastname']

    def __unicode__(self):
        return unicode(self.lastname + ", " + self.firstname + " (" + self.username + ")")

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'gtid', 'firstname', 'lastname', 'email', 'usertype')
    search_fields = ('username', 'gtid', 'firstname', 'lastname')
    list_filter = ('usertype', )

    actions = ['optin_program']

    def optin_program(self, request, queryset):
        opt_count = 0
        for s in queryset:
            if OptIn.objects.get_or_create(student=s, value=False)[1]:
                opt_count += 1

        self.message_user(request, "%d of %d students were put in the Opt In program." % (opt_count, len(queryset)) )

    optin_program.short_description = "Put in the Opt In program"

class OptIn(models.Model):
    student = models.ForeignKey(Student)
    value = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.student)

class OptInAdmin(admin.ModelAdmin):
    list_display = ('student', 'value')
    search_fields = ('student__username', 'student__firstname', 'student__lastname')
    list_filter = ('value', 'student__usertype')

    actions = ['optin', 'optout']

    def optin(self, request, queryset):
        for s in queryset:
            s.value = True
            s.save()

    optin.short_description = "Change to Opt-In"

    def optout(self, request, queryset):
        for s in queryset:
            s.value = False
            s.save()

    optout.short_description = "Change to Opt-Out"

class StudentLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student)
    details = models.CharField(default=None, max_length=1000)

    class Meta:
        ordering = ['created']

class StudentLogAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'details')
    search_fields = ('student__username', 'student__firstname', 'student__lastname', 'details')
    list_filter = ('created', )

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    gtid = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '987654321'}))
    fields = ('username', 'gtid')

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'pkolhe3'}))
    fields = ('username')
