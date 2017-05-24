from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from student.models import *
from assignment.models import *
from api.models import *
from student.log import *
from student.students_info import *

import json
import logging

log = logging.getLogger(__name__)

# Decorators
def check_permissions(perms):
    '''
    Checks if a key is valid or not.
    Use: @check_permissions("r"), @check_permissions(["r", "rw"])
    '''
    def wrapper(func):
        def validate(*args, **kwargs):
            response = {}
            if args:
                request = args[0]
                if request.method == 'GET':
                    key = request.GET.get('apikey', '')
                    try:
                        key = ApiKey.objects.get(key=key)
                        permission = key.permission
                        if permission in perms:
                            return func(*args, **kwargs)
                        else:
                            response['error'] = "Incorrect permissions"
                            return JsonResponse(response)

                    except Exception as e:
                        response['error'] = '%s' % (e.message)
                        return JsonResponse(response)
            return JsonResponse(response)
        return validate
    return wrapper

# Views
def index(request):
    response = {}
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))

    return JsonResponse(response)

def student(request, username):
    students = Student.objects.none()
    if request.method == 'GET':
        if name == "all":
            students = Student.objects.all()
        else:
            students = Student.objects.filter(username=username)

    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def assignment(request, a_name):
    a = Assignment.objects.none()
    if request.method == 'GET':
        if name == "all":
            a = Assignment.objects.all()
        else:
            a = Assignment.objects.filter(short_name=a_name)

        for _a in a:
            _a.url = "..." + _a.url[-25:]

    data = serializers.serialize('json', a)
    return HttpResponse(data, content_type='application/json')

def codework(request, a_name, username):
    response = {}
    if request.method == 'GET':
        io_solution = iosolution_info()
        if name == "all" and username == "all":
            io_solution.get()

        if name == "all":
            assignment = Assignment.objects.all()
        else:
            assignment = Assignment.objects.filter(short_name=name)
            io_solution.get_by_assignment(assignment)

        if username == "all":
            student = Student.objects.all()
        else:
            student = Student.objects.filter(username=username)
            io_solution.get_by_student(student)

        response_codework = io_solution.get_data()
        response['data'] = response_codework
        response['error'] = ""
        response['message'] = "Found codework of " + username + " in " + name
    return JsonResponse(response)

@check_permissions("r")
def update_codework(request, id):
    response = {}
    if request.method == 'GET':
        io_solution = iosolution_info()
        score = request.GET.get('score', '')
        comments = request.GET.get('comments', '')
        response['message'] = io_solution.update_notime(id, score, comments)
        response['error'] = ""
    return JsonResponse(response)
