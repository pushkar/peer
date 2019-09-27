from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django import template
from django_ajax.decorators import ajax
from django.forms.models import model_to_dict
from django.utils import timezone

from student.models import *
from exam.exam_info import *
import json


def index(request):
    s = Student.objects.get(username=request.session['user'])
    exams = Exam.objects.all()
    return render(request, 'exam_index.html', {
        'student': s,
        'exams': exams,
    })


def get_or_create_exam(request, exam_name):
    s = Student.objects.get(username=request.session['user'])
    e = exam_info(exam_name)
    if timezone.now() < e.exam.start_time:
        messages.warning(request, "Wait for exam to start.")
        return HttpResponseRedirect(reverse('exam:index'))
    if timezone.now() > e.exam.end_time:
        messages.warning(request, "Exam has ended.")
        return HttpResponseRedirect(reverse('exam:index'))
    tempexam = tempexam_info(s, e.get_exam())
    if tempexam.has_finished():
        messages.warning(request, "You submitted the exam.")
        return HttpResponseRedirect(reverse('exam:index'))
    return render(request, 'exam_get_or_create.html', {
        'student': s,
        'exam': e.get_exam(),
        'tempexam': tempexam.get_exam(),
    })


def save_exam(request, exam_name):
    s = Student.objects.get(username=request.session['user'])
    e = exam_info(exam_name)
    tempexam = tempexam_info(s, e.get_exam())
    if request.POST:
        data = dict(request.POST.iterlists())
        check, errors = tempexam.check_exam(data)
        if check is False:
            for id_, exp_ in errors.iteritems():
                errors_str = str(id_) + ". " + str(exp_)
                messages.warning(request, errors_str)
            messages.info(request, "Please correct all the warnings to submit the exam.")
        if data.has_key('save_button'):
            tempexam.save_exam(data)
            messages.success(request, "Your exam was saved successfully.")
        if check is True:
            if data.has_key('submit_button'):
                tempexam.save_exam(data)
                if tempexam.submit_exam():
                    messages.success(request, "Your exam was submitted successfully.")
                    tempexam.delete_exam()
                    return HttpResponseRedirect(reverse('exam:index'))
    return HttpResponseRedirect(reverse('exam:get_or_create_exam', args=[exam_name]))

# Redundant, the functionality is in save_exam()


def submit_exam(request, exam_name):
    s = Student.objects.get(username=request.session['user'])
    e = exam_info(exam_name)
    tempexam = tempexam_info(s, e.get_exam())
    if tempexam.submit_exam():
        messages.success(request, "Your exam was submitted successfully.")
        tempexam.delete_exam()
    return HttpResponseRedirect(reverse('exam:index'))


def admin_exam(request, exam_name):
    e = exam_info(exam_name)
    data = {}
    q_set = question_set_info(e.get_exam())
    for q in q_set.get_questions():
        data_q = {}
        data_q['question'] = model_to_dict(q, ['text', 'hardness'])
        data_q['answers'] = {}
        a_set = answer_set_info(q)
        for a in a_set.get_answers():
            data_q['answers'][a.id] = model_to_dict(a, ['id', 'label', 'text', 'correctness'])
        data[q.id] = data_q

    return render(request, 'exam_admin.html', {
        'exam': e.get_exam(),
        'data': data,
    })


@ajax
def graders(request, id):
    a = answer_info()
    a.get_answer_by_id(id)
    details = a.get_answer().details
    return render(request, 'exam_graders.html', {
        'data': details,
    })
