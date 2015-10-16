from django.contrib import admin
from record.models import *

class RecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'details')

class TopicGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group', 'order', 'name', 'details')

admin.site.register(Record, RecordAdmin)
admin.site.register(TopicGroup, TopicGroupAdmin)
admin.site.register(Topic, TopicAdmin)
