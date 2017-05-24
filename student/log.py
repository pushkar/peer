import logging
from django.utils import timezone
from student.models import StudentLog

log = logging.getLogger(__name__)

def log_login(s, new=False):
    log_ = StudentLog.objects.get_or_create(student=s, details="login")
    log.info("%s just logged in" % s)
    if log_[1] is False and new:
        log_[0].created = timezone.now()
        log_[0].save()

    return log_[0].created

def log_logout(s, new=False):
    log_ = StudentLog.objects.get_or_create(student=s, details="logout")
    log.info("%s just logged out" % s)
    if log_[1] is False and new:
        now = timezone.now()
        log_[0].created = now
        log_[0].save()
    return log_[0].created
