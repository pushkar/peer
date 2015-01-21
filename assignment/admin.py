from django.contrib import admin
from assignment.models import *

# Register your models here.
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentPage, AssignmentPageAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(StudentInfo, StudentInfoAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewText, ReviewTextAdmin)
