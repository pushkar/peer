from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django import template
from django_ajax.decorators import ajax

from student.models import *
from exam_info import *
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
    tempexam = tempexam_info(s, e.get_exam())
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
        tempexam.save_exam(data)
        messages.success(request, "Your exam was saved successfully.")
    return HttpResponseRedirect(reverse('exam:get_or_create_exam', args=[exam_name]))

def submit_exam(request, exam_name):
    s = Student.objects.get(username=request.session['user'])
    e = exam_info(exam_name)
    tempexam = tempexam_info(s, e.get_exam())
    if tempexam.submit_exam():
        messages.success(request, "Your exam was submitted successfully.")
        tempexam.delete_exam()
    return HttpResponseRedirect(reverse('exam:index'))
