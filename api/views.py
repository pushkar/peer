from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import JsonResponse
from student.models import *
from assignment.models import *
from api.models import *
from student.log import *

import json

def check_key(response, key_value):
    response['error'] = None
    #if ApiKey.objects.filter(key=key_value).count() < 1:
    #    response['error'] = "Key is Invalid"

def get_student(response, username):
    try:
        student = Student.objects.get(username=username)
    except Student.DoesNotExist:
        response['message'] += "No user with username " + username
        student = None

    return student

def get_assignment(response, short_name):
    try:
        assignment = Assignment.objects.get(short_name=short_name)
    except Assignment.DoesNotExist:
        response['message'] += "No assignment with short name " + short_name
        assignment = None

    return assignment

def index(request):
    response = {}
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))

    return JsonResponse(response)

def student(request, name):
    response = {}
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))

        if not response['error']:
            if name == "all":
                students = Student.objects.all()
            else:
                students = Student.objects.filter(username=name)

            response_students = {}
            for s in students:
                response_student_info = {}
                response_student_info['username'] = s.username
                response_student_info['gtid'] = s.gtid
                response_student_info['email'] = s.email
                response_student_info['lastname'] = s.lastname
                response_student_info['firstname'] = s.firstname
                response_students[s.username] = response_student_info
            response['data'] = response_students
            response['message'] = str(len(students)) + " students found"
    return JsonResponse(response)

def add_student(request):
    response = {}
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))
        if not response['error']:
            username = request.GET.get('username', '')
            gtid = request.GET.get('gtid', '')
            email = request.GET.get('email', '')
            usertype = request.GET.get('usertype', '')
            firstname = request.GET.get('firstname', '')
            lastname = request.GET.get('lastname', '')
            if len(username) > 0 and len(gtid) > 0:
                s, created = Student.objects.get_or_create(username=username, gtid=gtid)
                if len(s.email) == 0 and len(email) > 0:
                    s.email = email
                if len(s.firstname) == 0 and len(firstname) > 0:
                    s.firstname = firstname
                if len(s.lastname) == 0 and len(lastname) > 0:
                    s.lastname = lastname
                if len(s.usertype) == 0 and len(usertype) > 0:
                    s.usertype=usertype
                s.save()
                if created == True:
                    response['message'] = 'Created user ' + username
                else:
                    response['message'] = 'Updated user ' + username
            else:
                if len(username) == 0:
                    response['message'] = "No username for " + str(gtid)
                elif len(gtid) == 0:
                    response['message'] = "No GTID for " + str(username)
                else:
                    response['message'] = "No username and GTID given"

    return JsonResponse(response)

def add_submission(request):
    response = {}
    response['message'] = ""
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))
        if not response['error']:
            username = request.GET.get('username', '')
            student = get_student(response, username)

            short_name = request.GET.get('assignment', '')
            assignment = get_assignment(response, short_name)

            files = request.GET.get('files', '')
            if student and assignment and len(files) > 0:
                sub, created = Submission.objects.get_or_create(student=student, assignment=assignment)
                if len(sub.files) != len(files):
                    sub.files = files
                sub.save()
                if created == True:
                    response['message'] = 'Created submission for ' + username
                else:
                    response['message'] = 'Updated submission for ' + username
            else:
                response['message'] += ". Adding this submission failed"

    return JsonResponse(response)
