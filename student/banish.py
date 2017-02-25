import pytz
from django.contrib import messages
from django.utils import timezone
from student.models import *

MIN_TIME_BETWEEN_REQUESTS = 5 # in seconds
MAX_VIOLATIONS = 10

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def banish_check(request, s):
    is_banished = False
    banish, created = Banish.objects.get_or_create(student=s)
    if created:
        return is_banished
    banish.count = int(banish.count) + 1
    updated_time = banish.updated
    violations = int(banish.violations)
 
    current_time = timezone.now()
    # print "U " + str(updated_time)
    # print "C " + str(current_time)
    delta_time = current_time - updated_time
    # print "Delta is " + str(delta_time.seconds)
    if delta_time.seconds < MIN_TIME_BETWEEN_REQUESTS:
        banish.violations = int(banish.violations) + 1
    banish.save()

    if violations > MAX_VIOLATIONS:
        messages.info(request, "You have been banned for sending too many requests. Contact the TA.")
        return True
    return False
