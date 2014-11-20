from django.contrib import admin
from recommender.models import *
# Register your models here.

admin.site.register(StudentInfo, StudentInfoAdmin)
admin.site.register(Review, ReviewAdmin)
