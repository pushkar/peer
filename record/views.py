from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django_ajax.decorators import ajax

from record.models import *
from record.record_info import *
from student.views import *

def index(request):
    if not check_session(request):
            return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    record = record_info(s)
    record.get_record()
    record.details = record.get_details()
    return render(request, 'record_index.html', {
        'student': s,
        'record': record,
    })

def form(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])

    record = record_info(s)
    record.get_record()
    record.add_details(1, "Yes")

    record.details = record.get_details()

    return render(request, 'record_form.html', {
        'student': s,
        'record': record,
    })

def add(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    record = record_info(s)
    record.add_empty_record()
    return HttpResponseRedirect(reverse('record:index'))

#def update(request, topic_name, topic_detail):
