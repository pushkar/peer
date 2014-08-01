from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from mcscheme.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import numpy
import csv

#@login_required
def index(request):
  if len(request.user.username) == 0:
    return HttpResponse("No user is logged in.")
  return HttpResponse(request.user.username)

def home(request):
    request.session['student_id'] = 1
    s = Student.objects.get(pk=request.session['student_id'])
    r = "Student with email, " + s.email + ", is logged in"
    return HttpResponse(r)

def exam(request):
    message = ""
    if request.method == 'POST':
        form = TFForm(request.POST)
        if form.is_valid():
            tf = TFLog()
            tf.student_id = request.session['student_id']
            tf.question_id = request.session['question_id']
            tf.answer_tf = form.cleaned_data['answer_tf']
            tf.answer = form.cleaned_data['answer']
            tf.save()
            message = "Saved a TFLog at " + str(tf.created)

    q_s = Question.objects.all()
    q_list = range(0, q_s.count()-1)
    a_s = Answer.objects.filter(student_id=request.session['student_id'])
    for a in a_s:
        if a.question_id in q_list:
            q_list.remove(a.question_id)

    print q_list
    q_id = numpy.random.choice(q_list)
    request.session['question_id'] = q_id
    form = TFForm()

    return render(request, 'exam.html', {
        'message': message,
        'student': Student.objects.get(pk=request.session['student_id']),
        'question': request.session['question_id'],
        'form': form,
    })

def db_populate(request):
    response = ""
    open('djangotemp.txt', 'w')

    with open('roster.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if len(row) == 5:
                Student.objects.get_or_create(userid=row[0], email=row[1],
                    gtid=row[2], lastname=row[3], firstname=row[4])
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
