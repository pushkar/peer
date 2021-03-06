from django.contrib import admin
from exam.models import *

class ExamAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'start_time', 'end_time')

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('student', 'proficiency')
    search_fields = ('student__lastname', 'student__firstname', 'student__username')

class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'params')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'hardness', 'strategy')
    search_fields = ('text',)
    list_filter = ('exam',)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'label', 'text', 'correctness', 'student')
    search_fields = ('text', 'student')
    list_filter = ('question', 'finished')

class MCAdmin(admin.ModelAdmin):
    list_display = ('student', 'question')

class GradingAdmin(admin.ModelAdmin):
    list_display = ('student', 'grade', 'mc')

class TempExamAdmin(admin.ModelAdmin):
    list_display = ('pk', 'updated', 'student', 'exam', 'finished', 'details')
    list_filter = ('exam',)

admin.site.register(Exam, ExamAdmin)
admin.site.register(StudentInfo, StudentInfoAdmin)
admin.site.register(Strategy, StrategyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(MC, MCAdmin)
admin.site.register(Grading, GradingAdmin)
admin.site.register(TempExam, TempExamAdmin)
