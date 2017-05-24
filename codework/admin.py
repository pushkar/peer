import logging
from django.contrib import admin
from codework.models import IOSource, IOPair, IOSolution, IOSubmission
from codework.iosource_info import iosource_import_pairs

log = logging.getLogger(__name__)

class IOSourceAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'url')
    actions = ['import_pairs']

    def import_pairs(self, request, queryset):
        for query in queryset:
            log.info("Importing IOPairs for %s from %s" % (query.assignment, query.url))
            ret = iosource_import_pairs(query.assignment, query.url)
        self.message_user(request, "Imported %s IOPairs for %s." % (ret, query.assignment.name))
    import_pairs.short_description = "Import IO pairs from selected source"

class IOPairAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'input_av', 'output_av')
    list_filter = ('assignment__name', )

class IOSolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'assignment', 'created', 'updated', 'late_av', 'output_submitted_av', 'score')
    search_fields = ('id', 'student__lastname', 'student__firstname', 'student__username')
    list_filter = ('assignment__name', )

class IOSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score')
    list_filter = ('assignment__name',)

admin.site.register(IOSource, IOSourceAdmin)
admin.site.register(IOPair, IOPairAdmin)
admin.site.register(IOSolution, IOSolutionAdmin)
admin.site.register(IOSubmission, IOSubmissionAdmin)
