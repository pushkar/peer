from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from codework.models import *
from student.models import *
from assignment.models import *

from codework.iosolution_info import *
from codework.iosource_info import *

import urllib2
import random

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

    if not request.session['user']:
        return False
    return True

def index(request):
    return HttpResponse("codework")

def work(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))


    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)
    #import_pairs(a)
    pairs = solution_get(s, a, 3)

    return render(request, 'codework_work.html', {
            'student': s,
            'a': a,
            'a_name': a_name,
            'pairs': pairs,
        })
