import sys
import csv
import logging
import urllib3
from codework.models import IOSource
from django.contrib import messages
from codework.iopairs_info import pair_add

log = logging.getLogger(__name__)

def iosource_ifexists(a):
    if IOSource.objects.filter(assignment=a).count() > 0:
        return True
    return False

def iosource_import_pairs(a, url=None):
    count = 0
    csv.field_size_limit(sys.maxsize)
    try:
        if url is None:
            iosource = IOSource.objects.get(assignment=a)
            url = iosource.url
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        log.info("Download response status is %s" % response.status)
        rows = response.data.decode("utf-8")
        reader = csv.reader(rows.split('\n'), delimiter=';')
        for row in reader:
            if len(row) == 2:
                log.debug("Adding %s: %s" % (row[0], row[1]))
                if pair_add(a, row[0], row[1]):
                    count = count + 1
        log.info("Added %s IOPairs to %s" % (count, a))
        return count
    except Exception as e:
        log.error(e)
        return count
