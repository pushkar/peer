from django.contrib import admin
from record.models import *

class StudentDetailsAdmin(admin.ModelAdmin):
    list_display = ('student', 'profession', 'company', 'objectives')

class ObjectivesAdmin(admin.ModelAdmin):
    list_display = ('name',)

class RecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'assigned', 'details')

class TopicGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group', 'order', 'name', 'details')

admin.site.register(StudentDetails, StudentDetailsAdmin)
admin.site.register(Objectives, ObjectivesAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(TopicGroup, TopicGroupAdmin)
admin.site.register(Topic, TopicAdmin)