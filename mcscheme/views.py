from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from mcscheme.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import numpy

#@login_required
def index(request):
  if len(request.user.username) == 0:
    return HttpResponse("No user is logged in.")
  return HttpResponse(request.user.username)

def exam(request):
    student_id = 1
    message = ""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            a = Answer()
            a.student_id = form.cleaned_data['student_id']
            a.question_id = form.cleaned_data['question_id']
            a.answer = form.cleaned_data['answer']
            a.answer_tf = form.cleaned_data['answer_tf']
            a.save()
            message = "Success, saved answer."

    q_s = Question.objects.all()
    q_list = range(0, q_s.count()-1)
    a_s = Answer.objects.filter(student_id=student_id)
    for a in a_s:
        if a.question_id in q_list:
            q_list.remove(a.question_id)

    print q_list
    q_id = numpy.random.choice(q_list)
    form = ExamForm(initial={'student_id':student_id, 'question_id':q_id})

    return render(request, 'exam.html', {
        'message': message,
        'form': form,
    })

def db_populate(request):
    response = ""
    Student(email="abc").save()
    Student(email="def").save()
    response += "Students added<br />"

    Question(text="q1").save()
    Question(text="q2").save()
    Question(text="q3").save()
    Question(text="q4").save()
    Question(text="q5").save()
    Question(text="q6").save()
    response += "Questions added<br />"
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
