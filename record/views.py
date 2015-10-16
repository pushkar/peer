from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django_ajax.decorators import ajax

from record.models import *
from record.record_info import *
from student.views import *

def index(request):
    if not check_session(request):
            return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    record = record_info(s)
    record = record.get_details()
    print record

    return render(request, 'record_index.html', {
        'student': s,
        'record': record,
    })

def form(request, group):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])

    record = record_info(s)
    topics = topics_info()
    topics = topics.get_topics_by_group_id(group)
    topics_list = []
    for t in topics:
        t_dict = model_to_dict(t, fields=['id', 'name', 'details'])
        t_dict['user'] = record.get_topic_detail(t.pk)
        print t_dict['user']
        topics_list.append(t_dict)

    return render(request, 'record_form.html', {
        'student': s,
        'topics': topics_list,

    })

@ajax
def update(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    record = record_info(s)

    if request.POST:
        for topic_id, topic_detail in request.POST.iteritems():
            record.add_topic_detail(topic_id, topic_detail)
