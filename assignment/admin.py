import sys
import csv
import logging
import urllib3
import assignment.iopairs
from django.contrib import admin
from assignment.models import Assignment, AssignmentPage, IOPair, IOSolution

log = logging.getLogger(__name__)

def iosource_import_pairs(a):
    count = 0
    csv.field_size_limit(sys.maxsize)
    try:
        if a.url is None:
            message = "Assignment %s does not have url for codework" % a
            log.error(message)
            return message
        http = urllib3.PoolManager()
        response = http.request('GET', a.url)
        log.info("Download response status is %s" % response.status)
        rows = response.data.decode("utf-8")
        reader = csv.reader(rows.split('\n'), delimiter=';')
        for row in reader:
            if len(row) == 2:
                log.debug("Adding %s: %s" % (row[0], row[1]))
                if iopairs.add(a, row[0], row[1]):
                    count = count + 1
        message = "Added %s IOPairs to %s" % (count, a)
        return message
    except Exception as e:
        message = str(e)
        return message

# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date', 'released', 'enable_codework')

    actions = ['import_pairs']

    def import_pairs(self, request, queryset):
        for query in queryset:
            log.info("Importing IOPairs for %s from %s" % (query, query.url))
            ret = iosource_import_pairs(query)
        self.message_user(request, "%s" % (ret))
    import_pairs.short_description = "Import IO pairs from selected source"


class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

class IOPairAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'input_av', 'output_av')
    list_filter = ('assignment__name', )

class IOSolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'assignment', 'created', 'updated', 'late_av', 'output_submitted_av', 'score')
    search_fields = ('id', 'student__lastname', 'student__firstname', 'student__username')
    list_filter = ('assignment__name', )

# Register your models here.
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentPage, AssignmentPageAdmin)
admin.site.register(IOPair, IOPairAdmin)
admin.site.register(IOSolution, IOSolutionAdmin)
