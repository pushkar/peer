from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django_ajax.decorators import ajax

from student.models import *
from student.log import *
from assignment.models import *
from assignment.reviews_info import *

import StringIO
import csv
import datetime
import urllib2
import sendgrid

# Create your views here.
def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

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

@ajax
def messages_all(request):
    return render(request, 'messages.html', {})

def index(request):
    if check_session(request):
        s = Student.objects.get(username=request.session['user'])
        assignments = Assignment.objects.all()
        opt = OptIn.objects.get_or_create(student=s)
        opt_str = "opted out"
        if opt[0].value == True:
            opt_str = "opted in"
        return render(request, 'index.html', {
            'student': s,
            'assignments': assignments,
            'opt': opt_str,
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
                log_login(s, True)
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
        print s
        opt = OptIn.objects.get(student=s)
        opt.value = True
        opt.save()
        messages.success(request, "Your status was changed in the peer review program..")
    except Exception as e:
        print e
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))

def profile(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        assignments = Assignment.objects.all()
        opt = OptIn.objects.get(student=s)

        review_info = reviews_info()
        review_info.get_all_reviews()
        reviews = review_info.filter_by_student(s)
        reviews_data = review_info.get_data(reviews)
        assigned = review_info.filter_by_assigned(s)
        assigned_data = review_info.get_data(assigned)

        return render(request, 'profile.html', {
            'student': s,
            'assignments': assignments,
            'reviews_data': reviews_data,
            'assigned_data': assigned_data,
            'opt': opt,
        })

    except Exception as e:
        print e
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))

@ajax
def updates(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        assignments = Assignment.objects.all()

        data = {}
        reviews = Review.objects.filter(submission__student=s)
        for r in reviews:
            count = log_isread(s.username, r)
            if count != 0:
                data[r] = count

        reviews_assigned = Review.objects.filter(assigned=s)
        for r in reviews_assigned:
            count = log_isread(s.username, r)
            if count != 0:
                data[r] = count

        return render(request, 'updates.html', {
            'student': s,
            'assignments': assignments,
            'data': data,
        })


    except Exception as e:
        print e
        messages.warning(request, "Something went wrong. Let your TA know.")

    return HttpResponseRedirect(reverse('student:index'))



@login_required
def admin(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        s_all = Student.objects.all()
        return render(request, 'admin.html', {
            'student': s,
            'student_all': s_all,
        })

    except Exception as e:
        print e
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

@login_required
def populate(request):
    try:
        g = Global.objects.get(key="roster")
        roster_str = urllib2.urlopen(g.value).read()
        reader = csv.reader(roster_str.split('\n'), delimiter=',')
        total_count = 0
        added_count = 0
        for row in reader:
            if len(row) == 6:
                total_count += 1
                s = Student.objects.get_or_create(username=row[0], email=row[1],
                    gtid=row[2], usertype=row[3], lastname=row[4], firstname=row[5])
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

@login_required
def admin_review_assignments(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    try:
        s = Student.objects.get(username=request.session['user'])
        review_info = reviews_info()
        review_info.get_all_reviews()
        reviews_data = review_info.get_data()
        return render(request, 'admin_review_assignments.html', {
            'student': s,
            'reviews_data': reviews_data,
        })

    except Exception as e:
        print e
        messages.warning(request, "Something went wrong.")

    return HttpResponseRedirect(reverse('student:index'))
