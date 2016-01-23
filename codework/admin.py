from django.contrib import admin
from codework.models import *

admin.site.register(IOSource, IOSourceAdmin)
admin.site.register(IOPair, IOPairAdmin)
admin.site.register(IOSolution, IOSolutionAdmin)
admin.site.register(IOSubmission, IOSubmissionAdmin)
