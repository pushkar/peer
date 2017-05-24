from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.http import JsonResponse
from student.models import *
from assignment.models import *
from api.models import *
from codework.models import *
from student.log import *
from student.students_info import *
from codework.iosolution_info import *

import json

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

# Helpers
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

def get_submission(response, student, assignment):
    try:
        submission = Submission.objects.get(student=student, assignment=assignment)
    except Submission.DoesNotExist:
        if student is None:
            response['message'] = "Student does not exist"
        else:
            response['message'] += "Submission does not exist for " + student.username
        submission = None

    return submission

# Views
def index(request):
    response = {}
    if request.method == 'GET':
        check_key(response, request.GET.get('apikey', ''))

    return JsonResponse(response)

@check_permissions("r")
def student(request, name):
    response = {}
    if request.method == 'GET':
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

@check_permissions("r")
def add_student(request):
    response = {}
    if request.method == 'GET':
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
                s.usertype = usertype
            s.save()
            if created is True:
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

@check_permissions("r")
def update_student(request, name):
    response = {}
    if request.method == 'GET':
        try:
            s = Student.objects.get(username=name)
            if 'gtid' in request.GET:
                gtid = request.GET['gtid']
                s.gtid = gtid
            if 'firstname' in request.GET:
                firstname = request.GET['firstname']
                s.firstname = firstname
            if 'lastname' in request.GET:
                lastname = request.GET['lastname']
                s.lastname = lastname
            if 'usertype' in request.GET:
                usertype = request.GET['usertype']
                s.usertype = usertype
            if 'email' in request.GET:
                email = request.GET['email']
                s.email = email
            s.save()
            response['message'] = "Student Information updated"
        except ObjectDoesNotExist:
            response['message'] = "No student found"
        except MultipleObjectsReturned:
            response['message'] = "Mutliple students found with username"
    return JsonResponse(response)

@check_permissions("r")
def add_submission(request):
    response = {}
    response['message'] = ""
    if request.method == 'GET':
        username = request.GET.get('username', '')
        student = get_student(response, username)

        short_name = request.GET.get('assignment', '')
        assignment = get_assignment(response, short_name)

        files = request.GET.get('files', '')
        if student and assignment and len(files) > 0:
            sub, created = Submission.objects.get_or_create(student=student, assignment=assignment)
            sub.files = files
            sub.save()
            if created is True:
                response['message'] = 'Created submission for ' + username
            else:
                response['message'] = 'Updated submission for ' + username
        else:
            response['message'] += ". Adding this submission failed"
    return JsonResponse(response)

@check_permissions("r")
def add_review(request):
    response = {}
    response['message'] = ""
    if request.method == "GET":
        assignment_short_name = request.GET.get('assignment_short_name', '')
        submission_username = request.GET.get('submission_username', '')
        assigned_to_username = request.GET.get('assigned_to_username', '')
        assignment = get_assignment(response, assignment_short_name)
        student = get_student(response, submission_username)
        assigned_to = get_student(response, assigned_to_username)
        submission = get_submission(response, student, assignment)
        if submission and assigned_to:
            r, created = Review.objects.get_or_create(submission=submission, assigned=assigned_to)
            if created is True:
                response['message'] = "Created review for " + student.username
            else:
                response['message'] = "Review already assigned for " + submission_username

    return JsonResponse(response)

@check_permissions("r")
def update_review(request):
    response = {}
    response['message'] = ""
    if request.method == "GET":
        assignment_short_name = request.GET.get('assignment_short_name', '')
        submission_username = request.GET.get('submission_username', '')
        assigned_to_username = request.GET.get('assigned_to_username', '')
        score = request.GET.get('score', 0)
        comments = request.GET.get('comments', '')
        assignment = get_assignment(response, assignment_short_name)
        student = get_student(response, submission_username)
        assigned_to = get_student(response, assigned_to_username)
        submission = get_submission(response, student, assignment)
        if submission and assigned_to:
            r = Review.objects.get(submission=submission, assigned=assigned_to)
            if r:
                r.score = score
                r.save()
                if len(comments) > 0:
                    rc = ReviewConvo()
                    rc.review = r
                    rc.student = assigned_to
                    rc.text = comments
                    rc.save()
                response['message'] = "Created review for " + student.username
                response['message'] += ". Assigned score of " + str(score)
            else:
                response['message'] = "Failed to find review for " + submission_username

    return JsonResponse(response)

@check_permissions("r")
def get_review(request):
    response = {}
    response['message'] = ""
    if request.method == "GET":
        username = request.GET.get('submission_username', '')
        assignment_short_name = request.GET.get('assignment_short_name', '')

        try:
            student = Student.objects.get(username=username)
            assignment = Assignment.objects.get(short_name=assignment_short_name)
        except:
            response['message'] = "Incorrect username:" + username + " or assignment name:" + assignment_short_name
            return JsonResponse(response)

        ri = reviews_info()
        rci = review_convos_info()

        # reviews
        if assignment_short_name != '':
            reviews = ri.get_reviews_by_assignment(assignment)
        else:
            reviews = ri.get_all_reviews()

        if username != '':
            reviews = ri.filter_by_student(student, reviews)

        response['reviews'] = ri.serialize(reviews)

        #convos
        response['convos'] = {}
        for r in reviews:
            rci.get_convos_by_review(r)
            response['convos'][r.pk] = rci.serialize()

        response['error'] = ""
        # Use in the future
    return JsonResponse(response)

@check_permissions("r")
def codework(request, name, username):
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
