from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages

from student.models import *
import recommender.models as re

import StringIO
import csv
import datetime
import urllib2
import sendgrid

# Create your views here.
def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""

    if not request.session['user']:
        return False
    return True

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

def index(request):
    if check_session(request):
        s = Student.objects.get(username=request.session['user'])
        return render(request, 'index.html', {
            'student': s,
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
            print "Finding a user with " + str(username)

            try:
                s = Student.objects.get(username=username, gtid=gtid)
                print "Found"
                request.session['user'] = s.username
                messages.success(request, 'You are logged in.')
                return HttpResponseRedirect(reverse('student:index'))
            except Student.DoesNotExist:
                print "Not Found"
                messages.warning(request, "User does not exist. Try again.")
                return HttpResponseRedirect(reverse('student:index'))

    messages.warning(request, "Form entries are wrong. Please try again.")
    return HttpResponseRedirect(reverse('student:index'))

def pass_request(request):
    if request.method == 'POST':
        passform = ForgotPasswordForm(request.POST)
        if passform.is_valid():
            try:
                print "Finding user with " + passform.cleaned_data['username']
                s = Student.objects.get(username=passform.cleaned_data['username'])
                if send_email(s.email, s.gtid) == 200:
                    messages.success(request, "Sent a message with GTID to your GT email. Check your SPAM folder if you can't find it.")
                    return HttpResponseRedirect(reverse('student:pass_request'))
                else:
                    messages.warning(request, "Could not send an email. Contact your TA.")
                    return HttpResponseRedirect(reverse('student:pass_request'))
            except:
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
        return HttpResponseRedirect(reverse('student:index'))


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
        messages.success(request, "Thank you for opting in. You will soon have reviewers assigned to your submission.")
    except:
        messages.warning(request, "You should have reviews and reviewers assigned to you. Look in Assignments > Tasks. If not, wait for a few hours and check again.")

    return HttpResponseRedirect(reverse('student:index'))

@login_required
def populate(request):
    try:
        g = Global.objects.get(key="roster")
        roster_str = urllib2.urlopen(g.value).read()
        reader = csv.reader(roster_str.split('\n'), delimiter=',')
        total_count = 0
        added_count = 0
        for row in reader:
            if len(row) == 7:
                total_count += 1
                s = Student.objects.get_or_create(username=row[0], email=row[1],
                    gtid=row[2], usertype=row[3], lastname=row[4], firstname=row[5],
                    group_id=row[6])
                if s[1]:
                    added_count += 1

        messages.success(request, "%d of %d students were added." % (added_count, total_count))
    except:
        messages.info(request, "Could not find the roster.")


    return HttpResponseRedirect(reverse('admin:index'))

def group(request, group_id="1"):
    s = Student.objects.get(username=request.session['user'])
    s_g = Student.objects.filter(group_id=group_id)

    return render(request, 'group.html', {
        'student': s,
        'student_group': s_g,
    })
