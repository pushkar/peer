from django.contrib import admin
from django.http import HttpResponseRedirect

from student.models import *

# Register your models here.
admin.site.register(Global, GlobalAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(OptIn, OptInAdmin)
