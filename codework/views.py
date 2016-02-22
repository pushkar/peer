from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django_ajax.decorators import ajax
from django.contrib import messages
from django.utils import timezone, dateformat
from datetime import timedelta

from codework.models import *
from student.models import *
from assignment.models import *

from codework.iosolution_info import *
from codework.iosource_info import *

import urllib2
import random
import datetime

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

    if not request.session['user']:
        return False
    return True

def index(request):
    return HttpResponse("codework")

@login_required
def import_pairs(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)

    if s.usertype == "ta" or s.usertype == "superta":
        iosource_import_pairs(a)

    return HttpResponse("Imported for " + a.name)

@ajax
def work(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)

    deadline = a.due_date
    endline = deadline
    submit_late = False
    if a.end_date:
        endline = a.end_date
    if deadline > timezone.now():
        tl = deadline - timezone.now()
        time_left = "(" + str(tl.days) + " days, "
        time_left += str(tl.seconds/3600) + ":"
        time_left += str((tl.seconds%3600)/60) + " hours "
        time_left += " left)"
    elif timezone.now() < endline:
        tl = endline - timezone.now()
        time_left = "(" + str(tl.days) + " days, "
        time_left += str(tl.seconds/3600) + ":"
        time_left += str((tl.seconds%3600)/60) + " hours "
        time_left += " left to submit late)"
        submit_late = True
    else:
        time_left = "(Deadline Passed)"

    io_solution = iosolution_info()
    if iosource_ifexists(a):
        if a.short_name == "hw4":
            io_solution.generate(s, a, 1)
        else:
            io_solution.generate(s, a, 3)
    else:
        messages.info(request, "No coding excercises exist for this assignment.")

    solutions = io_solution.get_solutions()
    solutions_check = io_solution.check()

    solutions_dict = {}
    for s in io_solution.get_solutions():
        data = {}
        data['input'] = s.pair.input
        data['output_submitted'] = s.output_submitted
        data['check'] = solutions_check[s.pk]
        solutions_dict[s.pk] = data

    return render(request, 'codework_work.html', {
            'student': s,
            'a': a,
            'a_name': a_name,
            'solutions': solutions_dict,
            'deadline': deadline,
            'time_left': time_left,
            'submit_late': submit_late,
        })

@ajax
def update(request, id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    output_submitted = ""
    if request.method == "POST":
        output_submitted = request.POST.get("output", "")
        submit_late = request.POST.get("submit_late", "")
        ans = solution_update(id, output_submitted, submit_late)
        messages.success(request, ans)
