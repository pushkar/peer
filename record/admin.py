from django.contrib import admin
from record.models import *

# Register your models here.
admin.site.register(Record, RecordAdmin)
admin.site.register(Topic, TopicAdmin)
