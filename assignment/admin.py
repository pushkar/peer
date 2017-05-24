from django.contrib import admin
from assignment.models import Assignment, AssignmentPage

# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date', 'enable_submission', 'enable_peer_review', 'enable_codework', 'enable_stats')

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

# Register your models here.
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentPage, AssignmentPageAdmin)
