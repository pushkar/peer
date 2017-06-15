import json
import logging
import hashlib
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse
from django.core import serializers
from student.models import Student
from assignment.models import Assignment
import assignment.iosolutions as iosolutions
import assignment.iopairs as iopairs
from api.models import ApiKey

log = logging.getLogger(__name__)

# Decorators
def check_permissions(request):
    if request.method == 'GET':
        key = request.GET.get('key', '')
        log.info("GET key is %s" % key)

    if request.method == 'POST':
        key = request.POST.dict().get('key', '')
        log.info("POST key is %s" % key)

    apis = ApiKey.objects.filter(key=key)
    if len(apis) != 1:
        return False

    api = apis[0]
    api.count = api.count + 1
    api.save()
    timedelta = api.updated - api.created
    if timedelta.seconds > 300:
        api.delete()
        log.info("Revoked access for %s (%s seconds)" % (api.student, timedelta.seconds))
        return False
    return True

# Views
def index(request):
    response = {}
    response['message'] = "Call valid endpoints!"
    return JsonResponse(response)

@csrf_exempt
def login(request):
    data = {}
    student = Student.objects.none()
    if request.method == 'POST':
        student_count = Student.objects.filter(**request.POST.dict()).count()
        if student_count == 0:
            log.info("No student found with credentials %s" % request.POST.dict())
            data['error'] = "No student found with this login"
            return JsonResponse(data)
        if student_count > 1:
            log.info("Multiple students found with credentials %s" % request.POST.dict())
            data['error'] = "Multiple students found with this login (%s)" % student_count
            return JsonResponse(data)

        student = Student.objects.get(**request.POST.dict())
        if student.usertype != 'superta':
            log.info("%s does not have sufficient privileges to access API" % student)
            data['error'] = "You don't have sufficient privileges to access API"
            return JsonResponse(data)

        api_ = ApiKey.objects.get_or_create(student=student)
        if api_[1]:
            api = api_[0]
            permission = 'r'
            if student.usertype == 'superta':
                permission = 'w'
            hash_str = "%s%s" % (student, timezone.now())
            key = hashlib.sha224(hash_str.encode('utf-8')).hexdigest()
            api.key = key
            api.permission = permission
            api.save()
            log.info("Granted API access to %s at %s" % (student, api.created))
        else:
            api = api_[0]
            log.info("%s already had access. Logged into API again" % api.student)
        data = {}
        data['key'] = api_[0].key
    return JsonResponse(data)

def student_all(request):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    students = Student.objects.all()
    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def student_by_id(request, id):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    students = Student.objects.filter(pk=id)
    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

def student_by_user(request, username):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    students = Student.objects.filter(username=username)
    data = serializers.serialize('json', students)
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def student_add(request):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    if request.method == 'POST':
        data = request.POST.dict()
        if 'key' in data:
            del data['key']
        student = Student.objects.get_or_create(**data)
        if student[1]:
            log.info("Student %s created successfully" % student[0])
            return JsonResponse({'message': 'Student %s created' % student[0]})
        else:
            log.info("Could not create a user for %s" % data)
            return JsonResponse({'error': 'Could not create an entry for student with %s' % data})

def assignment_all(request):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    a = Assignment.objects.all()
    for _a in a:
        _a.url = "..." + _a.url[-25:]

    data = serializers.serialize('json', a)
    return HttpResponse(data, content_type='application/json')

def assignment(request, a_name):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    a = Assignment.objects.filter(short_name=a_name)
    for _a in a:
        _a.url = "..." + _a.url[-25:]

    data = serializers.serialize('json', a)
    return HttpResponse(data, content_type='application/json')

def codework(request, a_name, username):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    s = Student.objects.get(username=username)
    a = Assignment.objects.get(short_name=a_name)
    solutions = iosolutions.get_by(s, a)
    data = serializers.serialize('json', solutions)
    return HttpResponse(data, content_type='application/json')

def codework_by_username(request, username):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
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
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    solutions = iosolutions.get_none()
    try:
        if request.method == 'GET':
            a = Assignment.objects.get(short_name=a_name)
            solutions = iosolutions.get_by_assignment_all(a)
    except Exception as e:
        log.error(e)

    data = json.dumps(solutions)
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def iosolution_update(request, iosolution_id):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    if request.method == 'POST':
        data = request.POST.dict()
        if 'key' in data:
            del data['key']

        sol = iosolutions.get_by_id(iosolution_id)[0]

        if sol is None:
            return JsonResponse({'error': '(iosolution_update) No IOSolution found with id %s' % iosolution_id})

        if 'submission' in data:
            sol.output_submitted = data['submission']
        if 'comments' in data:
            sol.comments = data['comments']
        if 'score' in data:
            sol.score = data['score']
        sol.save()

        sol = iosolutions.get_by_id_all(iosolution_id)

        log.info("IOSolution %s saved" % iosolution_id)
        data = json.dumps(sol)
        return HttpResponse(data, content_type='application/json')

def codepair(request, id):
    if not check_permissions(request):
        return JsonResponse({'error': 'Permission Denied'})
    pair = iopairs.get_none()
    try:
        if request.method == 'GET':
            pair = iopairs.get_by_id(id)
    except Exception as e:
        log.error(e)

    data = serializers.serialize('json', pair)
    return HttpResponse(data, content_type='application/json')
