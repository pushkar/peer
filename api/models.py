from django.db import models

# Create your models here.
from django.contrib import admin, messages
from student.models import Student


class ApiKey(models.Model):
    student = models.ForeignKey(Student)
    key = models.CharField(max_length=200)
    permission = models.CharField(max_length=10, default="r")

    def __str__(self):
        return str("Key for " + unicode(self.student))

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('student', 'key', 'permission')
