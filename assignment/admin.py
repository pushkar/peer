from django.contrib import admin
from assignment.models import *

# Register your models here.
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentPage, AssignmentPageAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionFile, SubmissionFileAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(ReviewConvo, ReviewConvoAdmin)
