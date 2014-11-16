from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from ul.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import numpy
import csv

max_questions = 12

def index(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1

    if request.session['student_id'] != -1:
        s = Student.objects.get(pk=request.session['student_id'])
        return render(request, 'index.html', {
        'message': request.session['message'],
        'student': s,
    })
    else:
        form = LoginForm()
        return render(request, 'index.html', {
        'message': request.session['message'],
        'form': form,
    })


def exam_tf(request):
    if request.method == 'POST':
        form = TFForm(request.POST)
        if form.is_valid():
            log = Log()
            log.type_of_question = "tf"
            log.student_id = request.session['student_id']
            log.question_id = request.session['question_id']
            try:
                tf = TFLog.objects.get(student_id=request.session['student_id'], question_id=request.session['question_id'])
            except TFLog.DoesNotExist:
                tf = TFLog()
            tf.student_id = request.session['student_id']
            tf.question_id = request.session['question_id']
            tf.answer_tf = form.cleaned_data['answer_tf']
            tf.answer = form.cleaned_data['answer']
            tf.save()
            log.log_id = tf.pk
            log.save()
            if request.session['question_id'] < max_questions:
                request.session['question_id'] += 1
            return HttpResponseRedirect('/ul/exam')
        else:
            request.session['message'] = "Fill all required fields."
    return render(request, 'ulexam_tf.html', {
        'message': request.session['message'],
        'total': range(1, max_questions),
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
            try:
                mc = MCLog.objects.get(student_id=request.session['student_id'], question_id=request.session['question_id'])
            except MCLog.DoesNotExist:
                mc = MCLog()
            mc.student_id = request.session['student_id']
            mc.question_id = request.session['question_id']
            mc.answer1_id = request.session['answer1']
            mc.answer2_id = request.session['answer2']
            mc.choice = form.cleaned_data['choice']
            mc.save()
            log.log_id = mc.pk
            log.save()
            if request.session['question_id'] < max_questions:
                request.session['question_id'] += 1
            return HttpResponseRedirect('/ul/exam')
        else:
            request.session['message'] = "Choose an option before submitting."
    return render(request, 'ulexam_mc.html', {
        'message': request.session['message'],
        'total': range(1, max_questions),
        'question': Question.objects.get(pk=request.session['question_id']),
        'student': Student.objects.get(pk=request.session['student_id']),
        'answer1_tf': request.session['answer1_tf'],
        'answer2_tf': request.session['answer2_tf'],
        'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
        'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
        'form': form
    })

def exam_essay(request):
    if request.method == 'POST':
        form = ShortEssayForm(request.POST)
        if form.is_valid():
            try:
                e = ShortEssayLog.objects.get(student_id=request.session['student_id'], question_id=request.session['question_id'])
            except ShortEssayLog.DoesNotExist:
                e = ShortEssayLog()
            e.student_id = request.session['student_id']
            e.question_id = request.session['question_id']
            e.answer = form.cleaned_data['answer']
            e.save()
            if request.session['question_id'] < max_questions:
                request.session['question_id'] += 1
            return HttpResponseRedirect('/ul/exam')
        else:
            request.session['message'] = "Fill all required fields."
    return render(request, 'ulexam_essay.html', {
        'message': request.session['message'],
        'total': range(1, max_questions),
        'student': Student.objects.get(pk=request.session['student_id']),
        'question': Question.objects.get(pk=request.session['question_id']),
        'form': form,
    })

def exam(request):

    request.session['message'] = ""

    if Student.objects.get(pk=request.session['student_id']).gtpe_finished == 1:
        request.session['message'] = "You have finished and saved your exam. You can't visit it again."
        return HttpResponseRedirect("/sl")
    #----

    if int(request.session['question_id']) >= 9:
        try:
            log = ShortEssayLog.objects.filter(student_id=request.session['student_id'], question_id=request.session['question_id']).latest()
            data = {'answer': log.answer}
            form = ShortEssayForm(initial=data)

        except ShortEssayLog.DoesNotExist:
            form = ShortEssayForm()

        return render(request, 'ulexam_essay.html', {
            'message': request.session['message'],
            'total': range(1, max_questions),
            'student': Student.objects.get(pk=request.session['student_id']),
            'question': Question.objects.get(pk=request.session['question_id']),
            'form': form,
        })

    try:
        log = Log.objects.filter(student_id=request.session['student_id'], question_id=request.session['question_id']).latest()

        if log.type_of_question == "tf":
            tflog = TFLog.objects.get(pk=log.log_id)
            data = {'answer_tf': tflog.answer_tf, 'answer': tflog.answer}
            form = TFForm(initial=data)
            return render(request, 'ulexam_tf.html', {
                'message': request.session['message'],
                'total': range(1, max_questions),
                'student': Student.objects.get(pk=request.session['student_id']),
                'question': Question.objects.get(pk=request.session['question_id']),
                'form': form,
            })
        if log.type_of_question == "mc":
            mclog = MCLog.objects.get(pk=log.log_id)
            request.session['answer1'] = mclog.answer1_id
            request.session['answer2'] = mclog.answer2_id
            data = {'choice': mclog.choice}
            form = MCForm(initial=data)
            return render(request, 'ulexam_mc.html', {
                'message': request.session['message'],
                'total': range(1, max_questions),
                'student': Student.objects.get(pk=request.session['student_id']),
                'question': Question.objects.get(pk=request.session['question_id']),
                'answer1_tf': Answer.objects.get(pk=request.session['answer1']).answer_tf,
                'answer2_tf': Answer.objects.get(pk=request.session['answer2']).answer_tf,
                'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
                'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
                'form': form
            })

    except Log.DoesNotExist:
        pass

    #------

    if numpy.random.choice(2, 1)[0] == 0:
        form = TFForm()

        return render(request, 'ulexam_tf.html', {
            'message': request.session['message'],
            'total': range(1, max_questions),
            'student': Student.objects.get(pk=request.session['student_id']),
            'question': Question.objects.get(pk=request.session['question_id']),
            'form': form,
        })

    else:
        a_s = Answer.objects.filter(question_id=request.session['question_id'])
        if len(a_s) < 2:
            return HttpResponseRedirect('/ul/exam')
        a_s2 = numpy.random.choice(a_s, 2, False)
        request.session['answer1'] = a_s2[0].pk
        request.session['answer2'] = a_s2[1].pk
        request.session['answer1_tf'] = a_s2[0].answer_tf
        request.session['answer2_tf'] = a_s2[1].answer_tf

        form = MCForm()

        return render(request, 'ulexam_mc.html', {
            'message': request.session['message'],
            'total': range(1, max_questions),
            'student': Student.objects.get(pk=request.session['student_id']),
            'question': Question.objects.get(pk=request.session['question_id']),
            'answer1_tf': request.session['answer1_tf'],
            'answer2_tf': request.session['answer2_tf'],
            'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
            'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
            'form': form
        })

def update(request, q_id="1"):
    request.session['question_id'] = q_id
    return HttpResponseRedirect('/ul/exam')

def done(request):
    return render(request, 'uldone.html', {
      'message': request.session['message'],
      'student': Student.objects.get(pk=request.session['student_id']),
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
        a.count = 1
        a.save()
    s = Student.objects.get(pk=request.session['student_id'])
    s.gtpe_finished = 1
    s.save()
    request.session['message'] = "Congratulations, you have finished your exam."
    return HttpResponseRedirect("/sl")


@login_required
def db_populate(request):
    response = ""
    with open('roster.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if len(row) == 6:
                Student.objects.get_or_create(userid=row[0], email=row[1],
                    gtid=row[2], usertype=row[3], lastname=row[4], firstname=row[5], gtpe_finished=0)
                response += row[0] + " added.<br />"

    with open('questions2.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            Question.objects.get_or_create(question=row[1])
            response += row[0] + "<br />"

    with open('answers2.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            Answer.objects.get_or_create(question_id=row[0], student_id=1, answer_tf=row[1], answer=row[2], score=row[3], count=5)
            response += row[0] + "<br />"

    return HttpResponse(response)

@login_required
def db_show(request):
  response = ""
  s_entries = Student.objects.all()
  for s in s_entries:
      response += str(s.id) + ". " + str(s.email) + "<br />"

  response += "<hr />"

  q_entries = Question.objects.all()
  for q in q_entries:
    response += str(q.id) + ". " + str(q) + "<br />"

  response += "<hr />"
  a_entries = Answer.objects.all()
  for a in a_entries:
    response += str(a.question_id) + ". " + str(a.answer_tf) + "." + str(a.answer) + " (" + str(a.score) +")<br />"

  return HttpResponse(response)
