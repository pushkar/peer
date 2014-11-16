from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from sl.models import *

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
                return HttpResponseRedirect('/sl/')
            except Student.DoesNotExist:
                request.session['message'] = "User does not exist. Try again."
                return HttpResponseRedirect('/sl/')
    request.session['message'] = "Form entries are wrong. Please try again."
    return HttpResponseRedirect('/sl/')

def logout(request):
    if 'student_id' in request.session:
        request.session['student_id'] = -1
    request.session.flush()
    request.session['message'] = "You were successfully logged out."
    return HttpResponseRedirect('/sl')

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
            if request.session['question_id'] < 27:
                request.session['question_id'] += 1
            return HttpResponseRedirect('/sl/exam')
        else:
            request.session['message'] = "Fill all required fields."
    return render(request, 'exam_tf.html', {
        'message': request.session['message'],
        'total': range(1, 21),
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
            if request.session['question_id'] < 27:
                request.session['question_id'] += 1
            return HttpResponseRedirect('/sl/exam')
        else:
            request.session['message'] = "Choose an option before submitting."
    return render(request, 'exam_mc.html', {
        'message': request.session['message'],
        'total': range(1, 21),
        'question': Question.objects.get(pk=request.session['question_id']),
        'student': Student.objects.get(pk=request.session['student_id']),
        'answer1_tf': request.session['answer1_tf'],
        'answer2_tf': request.session['answer2_tf'],
        'answer1': Answer.objects.get(pk=request.session['answer1']).answer,
        'answer2': Answer.objects.get(pk=request.session['answer2']).answer,
        'form': form
    })

def exam(request):

    request.session['message'] = ""

    if Student.objects.get(pk=request.session['student_id']).gtpe_finished == 1:
        request.session['message'] = "You have finished and saved your exam. You can't visit it again."
        return HttpResponseRedirect("/sl")
    #----

    try:
        log = Log.objects.filter(student_id=request.session['student_id'], question_id=request.session['question_id']).latest()

        if log.type_of_question == "tf":
            tflog = TFLog.objects.get(pk=log.log_id)
            data = {'answer_tf': tflog.answer_tf, 'answer': tflog.answer}
            form = TFForm(initial=data)
            return render(request, 'exam_tf.html', {
                'message': request.session['message'],
                'total': range(1, 21),
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
            return render(request, 'exam_mc.html', {
                'message': request.session['message'],
                'total': range(1, 21),
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

        return render(request, 'exam_tf.html', {
            'message': request.session['message'],
            'total': range(1, 21),
            'student': Student.objects.get(pk=request.session['student_id']),
            'question': Question.objects.get(pk=request.session['question_id']),
            'form': form,
        })

    else:
        a_s = Answer.objects.filter(question_id=request.session['question_id'])
        if len(a_s) < 2:
            return HttpResponseRedirect('/sl/exam')
        a_s2 = numpy.random.choice(a_s, 2, False)
        request.session['answer1'] = a_s2[0].pk
        request.session['answer2'] = a_s2[1].pk
        request.session['answer1_tf'] = a_s2[0].answer_tf
        request.session['answer2_tf'] = a_s2[1].answer_tf

        form = MCForm()

        return render(request, 'exam_mc.html', {
            'message': request.session['message'],
            'total': range(1, 21),
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
    return HttpResponseRedirect('/sl/exam')

def done(request):
    return render(request, 'done.html', {
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
def grade_auto(request):
    mc_log = MCLog.objects.all()
    for m in mc_log:
        m.score = 0.0
        a1 = Answer.objects.get(pk=m.answer1_id)
        a2 = Answer.objects.get(pk=m.answer2_id)
        if a1.score == 1.0:
            if a2.score == 1.0:
                if m.choice == 3:
                    m.score = 1.0
            else:
                if m.choice == 1:
                    m.score = 1.0
        else:
            if a2.score == 1.0:
                if m.choice == 2:
                    m.score = 1.0
                else:
                    if m.choice == 4:
                        m.score = 0
        m.save()
    return render(request, 'index.html', {
      'message': request.session['message'],
    })

@login_required
def grade(request, log_type="tf", log_id="1", score=0.0):
    tf_log = TFLog.objects.get(pk=log_id)
    tf_log.score = score
    tf_log.save()
    return HttpResponseRedirect("/sl/grade/"+log_type+"/"+log_id)


@login_required
def grade_log(request, log_type="tf", log_id=1):
    request.session['message'] = ""
    try:
        if log_type == "tf":
            tf_log = TFLog.objects.get(pk=log_id)
            if tf_log.answer_tf == "1":
                answer_tf = "True"
            else:
                answer_tf = "False"
            student = Student.objects.get(pk=tf_log.student_id)
            question = Question.objects.get(pk=tf_log.question_id)
            back_link = "/sl/grade/"+log_type+"/"+str(int(log_id)-1)
            next_link = "/sl/grade/"+log_type+"/"+str(int(log_id)+1)
            return render(request, 'grade_tflog.html', {
                'message': request.session['message'],
                'tf_log' : tf_log,
                'answer_tf': answer_tf,
                'student': student,
                'question': question,
                'back': back_link,
                'next': next_link,
            })
        elif log_type == "mc":
            mc_log = MCLog.objects.get(pk=log_id)
            student = Student.objects.get(pk=mc_log.student_id)
            question = Question.objects.get(pk=mc_log.question_id)
            answer1 = Answer.objects.get(pk=mc_log.answer1_id)
            answer2 = Answer.objects.get(pk=mc_log.answer2_id)

            if answer1.answer_tf == "1":
                answer1_tf = "True"
            else:
                answer1_tf = "False"

            if answer2.answer_tf == "1":
                answer2_tf = "True"
            else:
                answer2_tf = "False"

            back_link = "/sl/grade/"+log_type+"/"+str(int(log_id)-1)
            next_link = "/sl/grade/"+log_type+"/"+str(int(log_id)+1)
            return render(request, 'grade_mclog.html', {
                'message': request.session['message'],
                'mc_log' : mc_log,
                'student': student,
                'question': question,
                'answer1': answer1,
                'answer2': answer2,
                'answer1_tf': answer1_tf,
                'answer2_tf': answer2_tf,
                'back': back_link,
                'next': next_link,
            })
    except:
        request.session['message'] = "Something went wrong"
        return render(request, 'grade_tflog.html', {
            'message': request.session['message'],
            'back': "javascript:history.go(-1)",
        })

@login_required
def grade_student(request, u_id="pushkar"):
    student = Student.objects.get(userid=u_id)
    log = Log.objects.filter(student_id=student.id)
    log_list = []
    for l in log:
        log_list.append([l.type_of_question, l.log_id])
    tflog = Log.objects.all()
    mclog = Log.objects.all()
    request.session['message'] = str(log.count())
    print log_list
    return render(request, 'grade.html', {
        'message': request.session['message'],
        'log': log_list,
        'tflog': tflog,
        'mclog': mclog,
        'student': student,
    })

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

    with open('questions.csv', 'rb') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            Question.objects.get_or_create(question=row[1])
            response += row[0] + "<br />"

    with open('answers.csv', 'rb') as file:
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
