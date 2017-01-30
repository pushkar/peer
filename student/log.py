from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import admin, messages

from student.models import *
from assignment.models import *
from datetime import datetime, tzinfo


def log_login(s, new=False):
    log = StudentLog.objects.get_or_create(student=s, details="login")
    if log[1] == False and new:
        log[0].created = timezone.now()
        log[0].save()
    return log[0].created

def log_logout(s, new=False):
    log = StudentLog.objects.get_or_create(student=s, details="logout")
    if log[1] == False and new:
        now = timezone.now()
        log[0].created = now
        log[0].save()
    return log[0].created

def log_review(username, review, new=False):
    review_details = "review_" + str(review.pk)
    s = Student.objects.get(username=username)
    log = StudentLog.objects.get_or_create(student=s, details=review_details)
    if log[1] == False and new:
        now = timezone.now()
        log[0].created = now
        log[0].save()
    return log[0].created

def log_isread(username, review):
    review_details = "review_" + str(review.pk)
    try:
        log = StudentLog.objects.get(student__username=username, details=review_details)
        return ReviewConvo.objects.filter(review=review, created__gt=log.created).count()
    except ReviewConvo.DoesNotExist:
        return -1
    except StudentLog.DoesNotExist:
        try:
            convo_count = ReviewConvo.objects.filter(review=review).count()
            if convo_count == 0:
                return -1
            return convo_count
        except:
            return -1
