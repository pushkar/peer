from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django_ajax.decorators import ajax
from django.contrib import messages
from django.utils import timezone, dateformat
from django.utils.translation import ngettext
from datetime import timedelta

from codework.models import *
from student.models import *
from assignment.models import *

from codework.iosolution_info import *
from codework.iosource_info import *
from student.banish import *

import urllib3
import random
import datetime

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

    if not request.session['user']:
        return False
    return True

def force_logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('student:index'))

def localize_timedelta(delta):
    ret = []
    num_years = int(delta.days / 365)
    if num_years > 0:
        delta -= timedelta(days=num_years * 365)
        ret.append(ngettext('%d year', '%d years', num_years) % num_years)

    if delta.days > 0:
        ret.append(ngettext('%d day', '%d days', delta.days) % delta.days)

    num_hours = int(delta.seconds / 3600)
    if num_hours > 0:
        delta -= timedelta(hours=num_hours)
        ret.append(ngettext('%d hour', '%d hours', num_hours) % num_hours)

    num_minutes = int(delta.seconds / 60)
    if num_minutes > 0:
        ret.append(ngettext('%d minute', '%d minutes', num_minutes) % num_minutes)

    return ' '.join(ret)

def index(request):
    return HttpResponse("codework")

def grade(request, a_name):
    io_solution = iosolution_info()
    a = Assignment.objects.get(short_name=a_name)
    io_solution.get_by_assignment(a)
    io_solution.check_notime()
    return HttpResponse("Grades done")

@login_required
def import_pairs(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)

    if s.usertype == "ta" or s.usertype == "superta":
        ret = iosource_import_pairs(a)

    return HttpResponse("Imported for " + a.name + "<br />" + str(ret))

@ajax
def work(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)

    deadline = a.due_date
    endline = deadline
    submit_late = False
    time_left = ""
    if a.end_date:
        endline = a.end_date
    if deadline > timezone.now():
        tl = deadline - timezone.now()
        time_left = "(%s left)" % localize_timedelta(tl)
    elif timezone.now() < endline:
        tl = endline - timezone.now()
        submit_late = True
        time_left = "(%s left)" % localize_timedelta(tl)
    else:
        time_left = "(Deadline Passed)"

    io_solution = iosolution_info()
    if iosource_ifexists(a):
        if a.short_name == "hw1":
            io_solution.generate(s, a, 10)
        elif a.short_name == "hw4":
            io_solution.generate(s, a, 1)
        else:
            io_solution.generate(s, a, 5)
    else:
        messages.info(request, "No coding excercises exist for this assignment.")

    solutions = io_solution.get_solutions()
    stats = io_solution.get_stats()

    return render(request, 'codework_work.html', {
        'student': s,
        'a': a,
        'a_name': a_name,
        'solutions': solutions,
        'deadline': deadline,
        'time_left': time_left,
        'submit_late': submit_late,
        'stats': stats,
        })

@ajax
def update(request, id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    if banish_check(request, s):
        force_logout(request)

    output_submitted = ""
    if request.method == "POST":
        output_submitted = request.POST.get("output", "")
        submit_late = request.POST.get("submit_late", "")
        io_solution = iosolution_info()
        ret = io_solution.update(id, output_submitted, submit_late)
        io_solution.check()
        messages.success(request, ret)
