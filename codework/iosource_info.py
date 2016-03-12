from django.contrib import messages
from codework.models import *
from codework.iopairs_info import *

import sys
import csv

def iosource_ifexists(a):
    if IOSource.objects.filter(assignment=a).count() > 0:
        return True
    return False


def iosource_import_pairs(a, url=None):
    ret = ""
    csv.field_size_limit(sys.maxsize)
    try:
        iosource = IOSource.objects.get(assignment=a)
        pairs_str = urllib2.urlopen(iosource.url).read()
        reader = csv.reader(pairs_str.split('\n'), delimiter=';')
        count = 0
        for row in reader:
            if len(row) == 2:
                print len(row[0])
                print len(row[1])
                if pair_add(a, row[0], row[1]):
                    count = count + 1
        ret += str(count) + " examples added to " + a.name
        ret += "<br />"
    except Exception as e:
        ret += '%s (%s)' % (e.message, type(e))
    finally:
        return ret
