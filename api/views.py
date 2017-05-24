import json
import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from student.models import Student
from assignment.models import Assignment
import assignment.iosolutions as iosolutions
import assignment.iopairs as iopairs
from api.models import ApiKey


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
    response['message'] = "Call valid endpoints!"
    return JsonResponse(response)

def students(request):
    students = Student.objects.none()
    try:
        students = Student.objects.all()
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def student_by_id(request, id):
    students = Student.objects.none()
    try:
        if request.method == 'GET':
            students = Student.objects.filter(pk=id)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def student_by_user(request, username):
    students = Student.objects.none()
    try:
        if request.method == 'GET':
            students = Student.objects.filter(username=username)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def assignment(request, a_name):
    a = Assignment.objects.none()
    try:
        if request.method == 'GET':
            if name == "all":
                a = Assignment.objects.all()
            else:
                a = Assignment.objects.filter(short_name=a_name)

            for _a in a:
                _a.url = "..." + _a.url[-25:]
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', a)
    return HttpResponse(data, content_type='application/json')

def codework(request, a_name, username):
    solutions = iosolutions.get_none()
    try:
        if request.method == 'GET':
            s = Student.objects.get(username=username)
            a = Assignment.objects.get(short_name=a_name)
            solutions = iosolutions.get_by(s, a)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', solutions)
    return HttpResponse(data, content_type='application/json')

def codework_by_username(request, username):
    solutions = iosolutions.get_none()
    try:
        if request.method == 'GET':
            s = Student.objects.get(username=username)
            solutions = iosolutions.get_by_student(s)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', solutions)
    return HttpResponse(data, content_type='application/json')

def codework_by_assignment(request, a_name):
    solutions = iosolutions.get_none()
    try:
        if request.method == 'GET':
            a = Assignment.objects.get(short_name=a_name)
            solutions = iosolutions.get_by_assignment(a)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', solutions)
    return HttpResponse(data, content_type='application/json')

def codepair(request, id):
    pair = iopairs.get_none()
    try:
        if request.method == 'GET':
            pair = iopairs.get_by_id(id)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', pair)
    return HttpResponse(data, content_type='application/json')
