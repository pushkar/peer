from django.db import models

# Create your models here.
from django.contrib import admin, messages
from student.models import *


class ApiKey(models.Model):
    student = models.ForeignKey(Student)
    key = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode("Key for " + unicode(self.student))

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('student', 'key')
