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
    return render(request, 'index.html', {
      'message': request.session['message'],
    })

def home(request):
    if 'student_id' in request.session:
        if request.session['student_id'] != -1:
            request.session['message'] = "You are already logged in. "
            return HttpResponseRedirect("/mcscheme/exam")
        else:
            request.session['student_id'] = -1
            request.session['message'] = "You are logged out. "
    else:
        request.session['student_id'] = -1
        request.session['message'] = "Welcome!"

    form = LoginForm()
    return render(request, 'login.html', {
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
                request.session['message'] = "Welcome " + s.firstname + " " + s.lastname + ","
                return HttpResponseRedirect('/mcscheme/exam')
            except Student.DoesNotExist:
                request.session['message'] = "User does not exist. Try again."
                return HttpResponseRedirect('/mcscheme/home')
    request.session['message'] = "Form entries are wrong. Please try again."
    return HttpResponseRedirect('/mcscheme/home')

def logout(request):
    if 'student_id' in request.session:
        request.session['student_id'] = -1
    request.session.flush()
    request.session['message'] = "You were successfully logged out."
    return HttpResponseRedirect('/mcscheme')

def exam_tf(request):
    if request.method == 'POST':
        form = TFForm(request.POST)
        if form.is_valid():
            log = Log()
            log.type_of_question = "tf"
            log.student_id = request.session['student_id']
            log.question_id = request.session['question_id']
            tf = TFLog()
            tf.student_id = request.session['student_id']
            tf.question_id = request.session['question_id']
            tf.answer_tf = form.cleaned_data['answer_tf']
            tf.answer = form.cleaned_data['answer']
            tf.save()
            log.log_id = tf.pk
            log.save()
            request.session['question_id'] += 1
            return HttpResponseRedirect('/mcscheme/exam')
        else:
            request.session['message'] = "Fill all required fields."
    return render(request, 'exam_tf.html', {
        'message': request.session['message'],
        'student': Student.objects.get(pk=request.session['student_id']),
        'question': Question.objects.get(pk=request.session['question_id']),
        'form': form,
    })


def exam_mc(request):
    if request.method == 'POST':
        form = MCForm(request.POST)
        if form.is_valid():
            log = Log()
            log.type_of_question = "mc"
            log.student_id = request.session['student_id']
            log.question_id = request.session['question_id']
            mc = MCLog()
            mc.student_id = request.session['student_id']
            mc.question_id = request.session['question_id']
            mc.answer1_id = request.session['answer1']
            mc.answer2_id = request.session['answer2']
            mc.choice = form.cleaned_data['choice']
            mc.save()
            log.log_id = mc.pk
            log.save()
            request.session['question_id'] += 1
            return HttpResponseRedirect('/mcscheme/exam')
        else:
            request.session['message'] = "Choose an option before submitting."
    return render(request, 'exam_mc.html', {
        'message': request.session['message'],
        'question': Question.objects.get(pk=request.session['question_id']),
        'answer1_tf': request.session['answer1_tf'],
        'answer2_tf': request.session['answer2_tf'],
        'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
        'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
        'form': form
    })

def exam(request):
    if Student.objects.get(pk=request.session['student_id']).gtpe_finished == 1:
        request.session['message'] = "You have finished and saved your exam. You can't visit it again."
        return HttpResponseRedirect("/mcscheme")

    if numpy.random.choice(2, 1)[0] == 0:
        form = TFForm()

        return render(request, 'exam_tf.html', {
            'message': request.session['message'],
            'student': Student.objects.get(pk=request.session['student_id']),
            'question': Question.objects.get(pk=request.session['question_id']),
            'form': form,
        })

    else:
        a_s = Answer.objects.filter(question_id=request.session['question_id'])
        if len(a_s) < 2:
            return HttpResponseRedirect('/mcscheme/exam')
        a_s2 = numpy.random.choice(a_s, 2, False)
        request.session['answer1'] = a_s2[0].pk
        request.session['answer2'] = a_s2[1].pk
        request.session['answer1_tf'] = a_s2[0].answer_tf
        request.session['answer2_tf'] = a_s2[1].answer_tf

        form = MCForm()

        return render(request, 'exam_mc.html', {
            'message': request.session['message'],
            'question': Question.objects.get(pk=request.session['question_id']),
            'answer1_tf': request.session['answer1_tf'],
            'answer2_tf': request.session['answer2_tf'],
            'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
            'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
            'form': form
        })

def update(request, q_id="1"):
    #Assume that the question_id is set somehow
    #try:
    #    log = Log.objects.get(student_id=request.session['student_id'], question_id=q_id)
    #
    #except Log.DoesNotExist:
    request.session['question_id'] = q_id
    return HttpResponseRedirect('/mcscheme/exam')

def done(request):
    return render(request, 'done.html', {
      'message': request.session['message'],
    })

def save(request):
    log = TFLog.objects.filter(student_id=request.session['student_id'])
    for l in log:
        try:
            a_old = Answer.objects.filter(student_id=request.session['student_id'], question_id=l.question_id)
            a_old.delete()
        except:
            pass
        a = Answer()
        a.student_id = l.student_id
        a.question_id = l.question_id
        a.answer_tf = l.answer_tf
        a.answer = l.answer
        a.save()
    s = Student.objects.get(pk=request.session['student_id'])
    s.gtpe_finished = 1
    s.save()
    request.session['message'] = "Congratulations, you have finished your exam."
    return HttpResponseRedirect("/mcscheme")

def db_populate(request):
    response = ""
    open('djangotemp.txt', 'w')

    with open('roster.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if len(row) == 5:
                Student.objects.get_or_create(userid=row[0], email=row[1],
                    gtid=row[2], lastname=row[3], firstname=row[4], gtpe_finished=0)
                response += row[0] + " added.<br />"

    with open('questions.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            Question.objects.get_or_create(text=row[0])
            response += row[0] + "<br />"

    return HttpResponse(response)

def db_show(request):
  response = ""
  s_entries = Student.objects.all()
  for s in s_entries:
      response += str(s.id) + ". " + str(s.email) + "<br />"

  response += "<hr />"

  q_entries = Question.objects.all()
  for q in q_entries:
    response += str(q.id) + ". " + str(q) + "<br />"
  return HttpResponse(response)
