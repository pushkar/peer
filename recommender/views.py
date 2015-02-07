from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from student.models import *
from assignment.models import *
from recommender.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import re
import numpy as np
import csv

a_name = "unsupervised"

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""

    if request.session['user'] == "":
        return False
    return True

def index(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    return HttpResponseRedirect('leaderboard')

def leaderboard(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    student = Student.objects.get(username=request.session['user'])
    score = Score.objects.filter(value__gt=0).order_by('value')

    try:
        a = Assignment.objects.get(short_name=a_name)
        ap = AssignmentPage.objects.filter(name=a_name)
    except:
        a = Assignment.objects.none()
        ap = AssignmentPage.objects.none()
        messages.info(request, 'Unsupervised Learning Assignment does not exist.')


    return render(request, 'recommender_leaderboard.html', {
        'student': student,
        'score': score,
        'assignment': a,
        'assignmentpages': ap,
        'a_name': a_name,
    })

def submit_prediction(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    student = Student.objects.get(username=request.session['user'])
    score = Score.objects.get_or_create(student=student)
    a = Assignment.objects.get(short_name=a_name)
    ap = AssignmentPage.objects.filter(name=a_name)

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        try:
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

                val = 0.0
                count = 0.0
                for i in range(1, 1000):
                    for j in range(1, 1700):
                        if test[i][j] != -1:
                            count = count + 1.0
                            if test_u[i][j] != -1:
                                val += (test[i][j]*test[i][j] - test_u[i][j]*test_u[i][j])
                            else:
                                val += 25

                score[0].value = round(0.2*np.sqrt(val/count), 4)
                score[0].save()
                messages.success(request, 'New score is %s.' % str(score[0].value))
            else:
                messages.info(request, 'Something went wrong.')
        except:
            messages.info(request, 'Something went wrong.')
    else:
        form = PredictionForm()

    return render(request, 'recommender_submitprediction.html', {
        'student': student,
        'score': score,
        'form': form,
        'assignment': a,
        'assignmentpages': ap,
        'a_name': a_name,
        })
