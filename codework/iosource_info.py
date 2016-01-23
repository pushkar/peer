from django.contrib import messages
from codework.models import *
from codework.iopairs_info import *

def iosource_ifexists(a):
    if IOSource.objects.filter(assignment=a).count() > 0:
        return True
    return False


def iosource_import_pairs(a, url=None):
    iosource = IOSource.objects.get(assignment=a)
    pairs_str = urllib2.urlopen(iosource.url).read()
    reader = csv.reader(pairs_str.split('\n'), delimiter=';')
    count = 0
    for row in reader:
        if len(row) == 2:
            if pair_add(a, row[0], row[1]):
                count = count + 1
    print str(count) + " examples added to " + a.name
