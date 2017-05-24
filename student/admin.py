import logging
from django.contrib import admin
from student.models import Student, StudentLog, StudentNotes, Banish

log = logging.getLogger(__name__)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'gtid', 'firstname', 'lastname', 'email', 'email_tsq', 'usertype')
    search_fields = ('username', 'gtid', 'firstname', 'lastname')
    list_filter = ('usertype', )

    actions = ['optin', 'optout']

    def optin(self, request, queryset):
        for s in queryset:
            s.optin = True
            s.save()
            log.info("%s changed to opt-in" % s)
        self.message_user(request, "Changed %s students to opt-in" % len(queryset))

    optin.short_description = "Change to Opt-In"

    def optout(self, request, queryset):
        for s in queryset:
            s.optin = False
            s.save()
            log.info("%s changed to opt-out" % s)
        self.message_user(request, "Changed %s students to opt-out" % len(queryset))

    optout.short_description = "Change to Opt-Out"

class StudentLogAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'details')
    search_fields = ('student__username', 'student__firstname', 'student__lastname', 'details')
    list_filter = ('created', )

class StudentNotesAdmin(admin.ModelAdmin):
    list_display = ('created', 'updated', 'student', 'notes')
    search_fields = ('student__username', 'student__firstname', 'student__lastname', 'notes')
    list_filter = ('student__username', )

class BanishAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'created', 'updated', 'ip', 'count', 'violations')
    search_fields = ('id', 'student__username', 'student__firstname', 'student__lastname', 'ip', 'count', 'violations')

# Register your models here.
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentLog, StudentLogAdmin)
admin.site.register(StudentNotes, StudentNotesAdmin)
admin.site.register(Banish, BanishAdmin)
