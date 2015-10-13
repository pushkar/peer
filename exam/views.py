from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django import template
from student.models import *

from django_ajax.decorators import ajax

from exam_info import *
import json

def index(request):
    s = Student.objects.get(username=request.session['user'])
    e = exam_info('midterm')
    tempexam = tempexam_info(s, e.get_exam())
    return render(request, 'exam_create.html', {
            'student': s,
            'exam': e.get_exam(),
            'tempexam': tempexam.create_exam(),
        })

def save_exam(request):
    print request.POST.lists()
    return HttpResponseRedirect(reverse('exam:index'))
