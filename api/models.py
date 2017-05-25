from django.db import models
from django.contrib import admin, messages
from student.models import Student

PERMISSION_TYPES = (
    ('r', 'Read Only'),
    ('w', 'Read/Write'),
)

class ApiKey(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    key = models.CharField(max_length=200, null=True)
    count = models.PositiveIntegerField(default=1)
    permission = models.CharField(max_length=10, choices=PERMISSION_TYPES, default='x')

    def __str__(self):
        return str("Key for %s " % self.student)

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('student', 'count', 'key', 'created', 'updated', 'permission')
