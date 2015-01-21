from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from student.models import *
from assignment.models import *
from recommender.models import *


from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import re
import numpy as np
import csv

def check_session(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    request.session['message'] = ""

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1

    if request.session['student_id'] == -1:
        return False
    return True

def index(request):
    if not check_session(request):
        return HttpResponseRedirect('/student/')

    return HttpResponseRedirect('leaderboard')

def leaderboard(request):
    if not check_session(request):
        return HttpResponseRedirect('/student/')

    s = Student.objects.get(pk=request.session['student_id'])
    si = StudentInfo.objects.filter(score__gt=0).order_by('score')
    a = Assignment.objects.filter(assignment_name="unsupervised")
    ap = AssignmentPage.objects.filter(assignment_name="unsupervised")

    return render(request, 'recommender_leaderboard.html', {
        'message': request.session['message'],
        'student': s,
        's_info': si,
        'assignment': a,
        'assignmentpages': ap,
    })

def submit_prediction(request):
    if not check_session(request):
        return HttpResponseRedirect('/student/')

    s = Student.objects.get(pk=request.session['student_id'])
    si = StudentInfo.objects.get(pk=request.session['student_id'])
    a = Assignment.objects.filter(assignment_name="unsupervised")
    ap = AssignmentPage.objects.filter(assignment_name="unsupervised")

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            test = np.full((1000, 1700), -1, dtype=np.int)
            test_u = np.full((1000, 1700), -1, dtype=np.int)

            with open('u_a.test', 'rb') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    if len(row) == 3:
                        test[int(row[0])][int(row[1])] = int(row[2])

            tuples = re.split(r'\n+', form.cleaned_data['test_data'])
            for row in tuples:
                n = re.split(r',+', row)
                if len(n) == 3:
                    test_u[int(n[0])][int(n[1])] = int(n[2])

            score = 0.0
            count = 0.0
            for i in range(1, 1000):
                for j in range(1, 1700):
                    if test[i][j] != -1:
                        count = count + 1.0
                        if test_u[i][j] != -1:
                            score += (test[i][j]*test[i][j] - test_u[i][j]*test_u[i][j])
                        else:
                            score += 25

            si.score = round(0.2*np.sqrt(score/count), 4)
            si.save()
            request.session['message'] = "New score is " + str(si.score)
        else:
            request.session['message'] = "Something went wrong."
    else:
        form = PredictionForm()

    return render(request, 'recommender_submitprediction.html', {
        'message': request.session['message'],
        'student': s,
        'si': si,
        'form': form,
        'assignment': a,
        'assignmentpages': ap,
        })

@login_required
def populate(request):
    students = Student.objects.all()
    for s in students:
        print s.pk
        si = StudentInfo()
        si.pk = s.pk
        si.userid = s.userid
        si.score = 0.0
        si.save()
    return HttpResponse("Done")
