from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from mcscheme.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import numpy
import csv

def index(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1

    if request.session['student_id'] != -1:
        s = Student.objects.get(pk=request.session['student_id'])
        return render(request, 'index_admin.html', {
        'message': request.session['message'],
        'student': s,
    })
    else:
        form = LoginForm()
        return render(request, 'index_admin.html', {
        'message': request.session['message'],
        'form': form,
    })

@login_required
def grade_all(request):
    request.session['message'] = ""
    students = Student.objects.all().order_by('lastname')
    scores = []
    for s in students:
        s_dict = {}
        tf_log = TFLog.objects.filter(student_id=s.pk)
        mc_log = MCLog.objects.filter(student_id=s.pk)
        n_score = 0
        for l in tf_log:
            if l.score > 0:
                n_score += l.score
        for l in mc_log:
            if l.score > 0:
                n_score += l.score
        s_dict['userid'] = s.userid
        s_dict['tf_count'] = tf_log.count()
        s_dict['mc_count'] = mc_log.count()
        s_dict['total_count'] = tf_log.count() + mc_log.count()
        s_dict['score'] = n_score
        scores.append(s_dict)
    return render(request, 'grade_all_admin.html', {
        'student': Student.objects.get(pk=request.session['student_id']),
        'message': request.session['message'],
        'scores': scores,
    })

@login_required
def questions_all(request):
    request.session['message'] = ""
    questions = Question.objects.all()

    return render(request, 'questions_all_admin.html', {
        'student': Student.objects.get(pk=request.session['student_id']),
        'message': request.session['message'],
        'questions': questions,
    })

@login_required
def question(request, q_id="1"):
    request.session['message'] = ""
    q = Question.objects.get(pk=q_id)

    tflog = TFLog.objects.filter(question_id=q_id)
    s = Student.objects.all()
    a = Answer.objects.all()

    return render(request, 'question_admin.html', {
        'student': Student.objects.get(pk=request.session['student_id']),
        'message': request.session['message'],
        'q': q,
        'a': a,
        's': s,
        'tflog': tflog,
    })
