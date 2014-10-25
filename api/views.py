import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from mcscheme.models import *

def index(request):
    response = {}
    return HttpResponse(json.dumps(response), content_type="application/json")

def student_obj_to_dict(s):
    s_dict = {}
    s_dict['pk'] = s.pk
    s_dict['userid'] = s.userid
    s_dict['firstname'] = s.firstname
    s_dict['lastname'] = s.lastname
    s_dict['gtpe_finished'] = s.gtpe_finished
    s_dict['usertype'] = s.usertype
    return s_dict

def question_obj_to_dict(q):
    q_dict = {}
    q_dict['pk'] = q.pk
    q_dict['text'] = q.question
    return q_dict

def answer_obj_to_dict(a):
    a_dict = {}
    if a.answer_tf == 1:
        a_dict['tf'] = "True"
    else:
        a_dict['tf'] = "False"
    a_dict['text'] = a.answer
    a_dict['score'] = a.score
    a_dict['student'] = student_obj_to_dict(Student.objects.get(pk=a.student_id))
    return a_dict

def student_all(request):
    response = {}
    students = Student.objects.all()
    for s in students:
        response[s.pk] = student_obj_to_dict(s)
    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")

def question_all(request):
    response = {}
    questions = Question.objects.all()
    for q in questions:
        response[q.pk] = question_obj_to_dict(q)
    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")

def answer_all(request):
    response = {}
    answers = Answer.objects.all()
    i = 1
    for a in answers:
        a_dict = {}
        a_dict['pk'] = a.pk
        a_dict['tf'] = a.answer_tf
        a_dict['text'] = a.answer
        a_dict['score'] = a.score
        s = Student.objects.get(pk=a.student_id)
        a_dict['student'] = student_obj_to_dict(s)
        response[i] = a_dict
        i = i + 1

    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")


def student(request, var="pk", val=""):
    response = {}
    if var=="pk":
        students = Student.objects.filter(pk=val)
    else:
        filter = var + '__' + 'contains'
        students = Student.objects.filter(**{ filter: val })
    for s in students:
        s_dict = {}
        s_dict['pk'] = s.pk
        s_dict['userid'] = s.userid
        s_dict['firstname'] = s.firstname
        s_dict['lastname'] = s.lastname
        s_dict['gtpe_finished'] = s.gtpe_finished
        response[s.pk] = s_dict

    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")


def tflog(request, q_id="1"):
    response = {}
    tflog = TFLog.objects.filter(question_id=q_id)

    i = 0
    for t in tflog:
        t_dict = {}
        t_dict['pk'] = t.pk
        t_dict['created'] = t.created.strftime('%m/%d/%Y')
        if t.answer_tf == 1:
            t_dict['tf'] = "True"
        else:
            t_dict['tf'] = "False"
        t_dict['text'] = t.answer
        t_dict['score'] = t.score
        t_dict['student'] = student_obj_to_dict(Student.objects.get(pk=t.student_id))
        t_dict['question'] = question_obj_to_dict(Question.objects.get(pk=q_id))
        response[i] = t_dict
        i = i + 1

    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")

def mclog(request, q_id="1"):
    response = {}
    mclog = MCLog.objects.filter(question_id=q_id)

    i=0
    for m in mclog:
        m_dict = {}
        m_dict['pk'] = m.pk
        m_dict['created'] = m.created.strftime('%m/%d/%Y')
        m_dict['choice'] = m.choice
        m_dict['score'] = m.score
        m_dict['question'] = question_obj_to_dict(Question.objects.get(pk=m.question_id))
        m_dict['student'] = student_obj_to_dict(Student.objects.get(pk=m.student_id))
        m_dict['answer1'] = answer_obj_to_dict(Answer.objects.get(pk=m.answer1_id))
        m_dict['answer2'] = answer_obj_to_dict(Answer.objects.get(pk=m.answer2_id))
        response[i] = m_dict
        i = i + 1

    return HttpResponse(json.dumps(response, indent=4), content_type="application/json")
