from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from student.models import *
from sl.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

from urllib2 import Request, urlopen, URLError

import numpy
import csv
import json

api_src = "http://localhost:8000/api/"

def index(request):
    if not 'message' in request.session:
        request.session['message'] = "Boo"

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1

    if request.session['student_id'] != -1:
        s = Student.objects.get(pk=request.session['student_id'])
        return render(request, 'grade_index.html', {
        'message': request.session['message'],
        'student': s,
    })
    else:
        form = LoginForm()
        return render(request, 'grade_index.html', {
        'message': request.session['message'],
        'form': form,
    })

@login_required
def grade_exam(request, exam):
    request.session['message'] = ""

    title = ""
    if exam == "sl":
        title = "Supervised Learning Exam"
    elif exam == "ul":
        title = "Unsupervised Learning Exam"
    elif exam == "rl":
        title = "Reinforcement Learning Exam"

    api_uri = api_src + str(exam) + "/q/all"
    api_request = Request(api_uri)
    response = urlopen(api_request)
    q_response = response.read()

    return render(request, 'grade_exam.html', {
        'title': title,
        'exam': exam,
        'message': request.session['message'],
        'student': Student.objects.get(pk=request.session['student_id']),
        'questions': json.loads(q_response),
    })

@login_required
def grade_question(request, exam, q_id="1"):
    request.session['message'] = ""

    title = ""
    if exam == "sl":
        title = "Supervised Learning Exam"
    elif exam == "ul":
        title = "Unsupervised Learning Exam"
    elif exam == "rl":
        title = "Reinforcement Learning Exam"

    api_uri = api_src + str(exam) + "/q/" + q_id
    api_request = Request(api_uri)
    response = urlopen(api_request)
    q_response = json.loads(response.read())

    if q_response['type'].strip() == "tf":
        api_uri = api_src + str(exam) + "/tflog/q/" + q_id

        api_request = Request(api_uri)
        response = urlopen(api_request)
        tf_response = response.read()

        api_uri = api_src + str(exam) + "/mclog/q/" + q_id

        api_request = Request(api_uri)
        response = urlopen(api_request)
        mc_response = response.read()

        request.session['refurl'] = "some url"
        return render(request, 'grade_tfquestion.html', {
            'title': title,
            'exam': api_src + str(exam),
            'message': request.session['message'],
            'student': Student.objects.get(pk=request.session['student_id']),
            'tf_response': json.loads(tf_response),
            'mc_response': json.loads(mc_response),
        })

    elif q_response['type'].strip() == "short":

        api_uri = api_src + str(exam) + "/selog/q/" + q_id

        api_request = Request(api_uri)
        response = urlopen(api_request)
        s_response = response.read()

        request.session['refurl'] = "some url"
        return render(request, 'grade_shortquestion.html', {
            'title': title,
            'exam': api_src + str(exam),
            'message': request.session['message'],
            'student': Student.objects.get(pk=request.session['student_id']),
            's_response': json.loads(s_response),
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

    api_uri = "http://localhost:8000/api/tflog/" + q_id
    api_request = Request(api_uri)
    response = urlopen(api_request)
    tf_response = response.read()

    api_uri = "http://localhost:8000/api/mclog/" + q_id
    api_request = Request(api_uri)
    response = urlopen(api_request)
    mc_response = response.read()

    return render(request, 'question_admin.html', {
        'message': request.session['message'],
        'student': Student.objects.get(pk=request.session['student_id']),
        'tf_response': json.loads(tf_response),
        'mc_response': json.loads(mc_response),
    })

@login_required
def tflog_update(request, id="0", score="0.0"):
    request.session['message'] = ""

@login_required
def mclog_update(request, id="0", score="0.0"):
    request.session['message'] = ""
