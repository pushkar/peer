from django.contrib import admin
from sl.models import *
# Register your models here.

admin.site.register(StudentInfo, StudentInfoAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(TFLog, TFLogAdmin)
admin.site.register(MCLog, MCLogAdmin)
