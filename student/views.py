from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages

from student.models import *
import recommender.models as re

import StringIO
import csv
import datetime
import urllib2

# Create your views here.

def index(request):
    if not 'user' in request.session:
        request.session['user'] = ""

    if request.session['user']:
        s = Student.objects.get(username=request.session['user'])

        return render(request, 'index.html', {
        'student': s,
    })
    else:
        form = LoginForm()
        return render(request, 'index.html', {
        'form': form,
    })

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            gtid = form.cleaned_data['gtid']
            print "Finding a user with " + str(username)
            try:
                s = Student.objects.get(username=username, gtid=gtid)
                request.session['user'] = s.username
                messages.success(request, 'You are logged in.')
                return HttpResponseRedirect(reverse('student:index'))
            except Student.DoesNotExist:
                messages.warning(request, "User does not exist. Try again.")
                return HttpResponseRedirect(reverse('student:index'))
    messages.warning(request, "Form entries are wrong. Please try again.")
    return HttpResponseRedirect(reverse('student.views.index'))

def logout(request):
    if 'user' in request.session:
        request.session['user'] = ""
    request.session.flush()
    messages.success(request, "You were successfully logged out")
    return HttpResponseRedirect(reverse('student:index'))


@login_required
def populate(request):
    try:
        g = Global.objects.get(key="roster")
        roster_str = urllib2.urlopen(g.value).read()
        reader = csv.reader(roster_str.split('\n'), delimiter=',')
        total_count = 0
        added_count = 0
        for row in reader:
            if len(row) == 7:
                total_count += 1
                s = Student.objects.get_or_create(username=row[0], email=row[1],
                    gtid=row[2], usertype=row[3], lastname=row[4], firstname=row[5],
                    group_id=row[6])
                if s[1]:
                    added_count += 1

        messages.success(request, "%d of %d students were added." % (added_count, total_count))
    except:
        messages.info(request, "Could not find the roster.")


    return HttpResponseRedirect(reverse('admin:index'))

@login_required
def group(request, group_id="1"):
    s = Student.objects.get(username=request.session['user'])
    s_g = Student.objects.filter(group_id=group_id)

    return render(request, 'group.html', {
        'student': s,
        'student_group': s_g,
    })
