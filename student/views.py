import os
import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_ajax.decorators import ajax

import student.utils as utils
import student.log as log_entry
import student.banish as banish
from student.models import Student, LoginForm, ForgotPasswordForm
from assignment.models import Assignment

import sendgrid

log = logging.getLogger(__name__)

# Create your views here.
def send_email(email, gtid):
    env_sendgrid_user = os.environ.get('ENV_SENDGRID_USER')
    env_sendgrid_pass = os.environ.get('ENV_SENDGRID_PASS')
    if env_sendgrid_user is None:
        log.error('Sendgrid username not set. Set enviornment variable ENV_SENDGRID_USER')
        return False
    if env_sendgrid_pass is None:
        log.error('Sendgrid password not set. Set enviornment variable ENV_SENDGRID_PASS')
        return False
    sg = sendgrid.SendGridClient(env_sendgrid_user, env_sendgrid_pass)
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject('Password Reset')
    message.set_text('Your GTID is ' + gtid)
    message.set_from('GTML TAs ')
    status, msg = sg.send(message)
    return status

def get_student_data(request):
    data = {}
    username = request.session['user']
    usertype = request.session['usertype']
    data['student'] = Student.objects.get(username=username)
    data['assignments'] = Assignment.objects.all()
    if usertype == 'student':
        data['assignments'] = data['assignments'].filter(released=True)
    return data

@ajax
def messages_all(request):
    return render(request, 'messages.html', {})

def index(request):
    if utils.check_session(request):
        return render(request, 'index.html', {
            **get_student_data(request),
        })
    else:
        form = LoginForm()
        return render(request, 'index.html', {
            'form': form,
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
                log_entry.log_login(s, True)
                if banish.banish_check(request, s):
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
            'passform': passform,
        })


def logout(request):
    if 'user' in request.session:
        request.session['user'] = ""
    request.session.flush()
    messages.success(request, "You were successfully logged out")
    return HttpResponseRedirect(reverse('student:index'))

def optin(request):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    s.optin = True
    s.save()
    log.info("%s changed to opt-in" % s)
    return HttpResponseRedirect(reverse('student:index'))

def profile(request):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    return render(request, 'profile.html', {
        **get_student_data(request),
    })

def about(request):
    assignments = Assignment.objects.none()
    if 'usertype' in request.session:
        if len(request.session['usertype']) > 0:
            if request.session['usertype'] == 'student':
                assignments = Assignment.objects.filter(released=True)
            else:
                assignments = Assignment.objects.all()

    return render(request, 'about.html', {
        'assignments': assignments,
    })

@login_required
def admin(request):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    student_all = Student.objects.all()
    return render(request, 'admin.html', {
        **get_student_data(request),
        'student_all': student_all,
    })


@login_required
def login_change(request, user):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=user)
    request.session['user_original'] = request.session['user']
    request.session['user'] = s.username
    request.session['usertype'] = s.usertype
    log.critical("%s changed login to %s" % (request.session['user_original'], s))
    messages.success(request, 'You are now logged in as %s' % s)

    return HttpResponseRedirect(reverse('student:index'))
