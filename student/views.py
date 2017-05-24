from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django_ajax.decorators import ajax
from django.template.defaulttags import register

from student.models import *
from student.log import *
from student.banish import *
from student.common import *
from assignment.models import *

import csv
import datetime
import urllib3
import sendgrid

log = logging.getLogger(__name__)

# Create your views here.
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def send_email(email, gtid):
    sendgrid_user = ""
    sendgrid_pass = ""
    g = Global.objects.all()
    for g_entry in g:
        if g_entry.key == "sendgrid_user":
            sendgrid_user = g_entry.value
        if g_entry.key == "sendgrid_pass":
            sendgrid_pass = g_entry.value

    sg = sendgrid.SendGridClient(sendgrid_user, sendgrid_pass)
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject('Password Reset')
    message.set_text('Your GTID is ' + gtid)
    message.set_from('GTML TAs ')
    status, msg = sg.send(message)
    return status

@ajax
def messages_all(request):
    return render(request, 'messages.html', {})

def index(request):
    if check_session(request):
        s = Student.objects.get(username=request.session['user'])
        assignments = Assignment.objects.all()
        opt = OptIn.objects.get_or_create(student=s)
        opt_str = "opted out"
        if opt[0].value is True:
            opt_str = "opted in"
        return render(request, 'index.html', {
            'student': s,
            'assignments': assignments,
            'opt': opt_str,
            'global': get_global(),
        })
    else:
        form = LoginForm()
        return render(request, 'index.html', {
            'form': form,
            'global': get_global(),
        })

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            gtid = form.cleaned_data['gtid']
            try:
                s = Student.objects.get(username=username, gtid=gtid)
                request.session['user'] = s.username
                request.session['usertype'] = s.usertype
                log_login(s, True)
                if banish_check(request, s):
                    messages.info(request, "You have been banned. Contact the TA.")
                    request.session.flush()
                    return HttpResponseRedirect(reverse('student:index'))
                messages.success(request, 'You are logged in.')
                return HttpResponseRedirect(reverse('student:index'))
            except Student.DoesNotExist:
                messages.warning(request, "User does not exist. Try again.")
                return HttpResponseRedirect(reverse('student:index'))

    messages.warning(request, "Form entries are wrong. Please try again.")
    return HttpResponseRedirect(reverse('student:index'))

def pass_request(request):
    if request.method == 'POST':
        passform = ForgotPasswordForm(request.POST)
        if passform.is_valid():
            try:
                s = Student.objects.get(username=passform.cleaned_data['username'])
                if send_email(s.email, s.gtid) == 200:
                    messages.success(request, "Sent a message with GTID to your GT email. Check your SPAM folder if you can't find it.")
                    return HttpResponseRedirect(reverse('student:pass_request'))
                else:
                    messages.warning(request, "Could not send an email. Contact your TA.")
                    return HttpResponseRedirect(reverse('student:pass_request'))
            except Exception as e:
                log.error(e)
                messages.warning(request, "Could not find user. Try again!")
                return HttpResponseRedirect(reverse('student:pass_request'))
        else:
            messages.warning(request, "Username not valid. Try again!")

        return HttpResponseRedirect(reverse('student:pass_request'))

    else:
        passform = ForgotPasswordForm()
        return render(request, 'index.html', {
            'global': get_global(),
            'passform': passform,
        })


def logout(request):
    if 'user' in request.session:
        request.session['user'] = ""
    request.session.flush()
    messages.success(request, "You were successfully logged out")
    return HttpResponseRedirect(reverse('student:index'))

def optin(request):
    if check_session(request):
        s = Student.objects.get(username=request.session['user'])

    try:
        opt = OptIn.objects.get(student=s)
        opt.value = True
        opt.save()
        messages.success(request, "Your status was changed in the peer review program..")
    except Exception as e:
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))

def profile(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        assignments = Assignment.objects.all()
        opt = OptIn.objects.get(student=s)

        return render(request, 'profile.html', {
            'global': get_global(),
            'student': s,
            'assignments': assignments,
            'opt': opt,
        })

    except Exception as e:
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))

def about(request):
    try:
        assignments = Assignment.objects.all()

        return render(request, 'about.html', {
            'assignments': assignments,
        })

    except Exception as e:
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))


@login_required
def admin(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        a = Assignment.objects.all()
        s_all = Student.objects.all()
        return render(request, 'admin.html', {
            'global': get_global(),
            'student': s,
            'assignments': a,
            'student_all': s_all,
        })

    except Exception as e:
        messages.warning(request, "Something went wrong.")

    return HttpResponseRedirect(reverse('student:index'))

@login_required
def login_change(request, user):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=user)
    request.session['user'] = s.username
    request.session['usertype'] = s.usertype

    return HttpResponseRedirect(reverse('student:admin'))
