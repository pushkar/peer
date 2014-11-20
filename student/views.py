from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from student.models import *
import sl.models as sl
import ul.models as ul
import rl.models as rl

import csv
import datetime

# Create your views here.

def index(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1

    if request.session['student_id'] != -1:
        s = Student.objects.get(pk=request.session['student_id'])
        sl_info = sl.ExamInfo.objects.get(pk=1)
        ul_info = ul.ExamInfo.objects.get(pk=1)
        rl_info = rl.ExamInfo.objects.get(pk=1)

        sl_link = ""
        ul_link = ""
        rl_link = ""

        now = datetime.datetime.now()

        if sl_info.starttime.replace(tzinfo=None) > now:
            sl_link = sl_info.name + " will start in " + str(sl_info.starttime.replace(tzinfo=None) - now) + " hours"
        elif sl_info.stoptime.replace(tzinfo=None) < now:
            sl_link = sl_info.name + " (Exam Ended) "
        else:
            sl_link = "<a href='/sl'>" + sl_info.name + "</a>"

        if ul_info.starttime.replace(tzinfo=None) > now:
            ul_link = ul_info.name + " will start in " + str(sl_info.starttime.replace(tzinfo=None) - now) + " hours"
        elif ul_info.stoptime.replace(tzinfo=None) < now:
            ul_link = ul_info.name + " (Exam Ended) "
        else:
            ul_link = "<a href='/ul'>" + ul_info.name + "</a>"

        if rl_info.starttime.replace(tzinfo=None) > now:
            rl_link = rl_info.name + " will start in " + str(rl_info.starttime.replace(tzinfo=None) - now) + " hours"
        elif rl_info.stoptime.replace(tzinfo=None) < now:
            rl_link = rl_info.name + " (Exam Ended) "
        else:
            rl_link = "<a href='/rl'>" + rl_info.name + "</a>"


        return render(request, 'index.html', {
        'message': request.session['message'],
        'student': s,
        'sl_link': sl_link,
        'ul_link': ul_link,
        'rl_link': rl_link,
    })
    else:
        form = LoginForm()
        return render(request, 'index.html', {
        'message': request.session['message'],
        'form': form,
    })

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            userid = form.cleaned_data['userid']
            gtid = form.cleaned_data['gtid']
            print "Finding a user with " + str(userid)
            try:
                s = Student.objects.get(userid=userid, gtid=gtid)
                request.session['student_id'] = s.pk
                request.session['question_id'] = 1
                request.session['message'] = "You are logged in."
                return HttpResponseRedirect('/student/')
            except Student.DoesNotExist:
                request.session['message'] = "User does not exist. Try again."
                return HttpResponseRedirect('/sl/')
    request.session['message'] = "Form entries are wrong. Please try again."
    return HttpResponseRedirect('/student/')

def logout(request):
    if 'student_id' in request.session:
        request.session['student_id'] = -1
    request.session.flush()
    request.session['message'] = "You were successfully logged out."
    return HttpResponseRedirect('/student')


@login_required
def populate(request):
    response = ""
    with open('roster.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if len(row) == 6:
                Student.objects.get_or_create(userid=row[0], email=row[1],
                    gtid=row[2], usertype=row[3], lastname=row[4], firstname=row[5])
                response += row[0] + " added.<br />"

    return HttpResponse(response)
