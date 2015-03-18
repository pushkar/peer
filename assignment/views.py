from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from assignment.models import *
from student.models import *
from student.log import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django_ajax.decorators import ajax

import re
import numpy as np
import csv
import json

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

    if not request.session['user']:
        return False
    return True

# Displays all Assignments
def index(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.all()

    return render(request, 'assignment_index.html', {
            'student': s,
            'assignments': a,
        })

# Displays a page from the database
@ajax
def page(request, a_name, p_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)
    ap = AssignmentPage.objects.filter(assignment=a)
    ap_this = ap.filter(name=p_name)

    return render(request, 'assignment_pageview.html', {
            'student': s,
            'assignment': a,
            'ap': ap,
            'ap_this': ap_this,
            'a_name': a_name,
        })


@ajax
def stats(request, a_name):
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)
    convos = ReviewConvo.objects.all()

    word_count = {}
    for c in convos:
        count = len(c.text.split())
        count = count / 100 * 100
        count += 99
        if word_count.has_key(count):
            word_count[count] += 1
        else:
            word_count[count] = 1

    submission_count = Submission.objects.all().count()
    review_count = len(convos)
    optin_count = OptIn.objects.filter(value=True).count()
    optout_count = OptIn.objects.filter(value=False).count()-20

    return render(request, 'assignment_stats.html', {
            'a_name': a_name,
            'ap': ap,
            'wc': word_count,
            'optin': optin_count,
            'optout': optout_count,
            'submission_count': submission_count,
            'review_count': review_count,
        })

# Default view for assignments
# Enlists tasks
def home(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    extra_scripts = ""
    if request.method == "GET":
        if request.GET.has_key('page'):
            p_name = request.GET['page']
            extra_scripts = "load_div(\'"+ reverse('assignment:page', args=[a_name, p_name]) +"\', \'#assignment_content\'); \n"

        if request.GET.has_key('review'):
            review_pk = request.GET['review']
            extra_scripts = "load_div(\'"+ reverse('assignment:review', args=[a_name, review_pk]) +"\', \'#assignment_content\'); \n"

    username = request.session['user']
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)

    print extra_scripts

    return render(request, 'assignment_pagebase.html', {
        'ap': ap,
        'a_name': a_name,
        'extra_scripts': extra_scripts,
    })

@ajax
def review(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session["user"]
    usertype = request.session["usertype"]
    review = Review.objects.get(pk=id)

    allowed = False
    if review.submission.student.username == username or review.assigned.username == username:
        allowed = True

    if not allowed:
        try:
            permissions = Permission.objects.get(review=review, student__username=username)
            allowed = True
        except:
            allowed = False

    if not allowed:
        messages.info(request, 'You are not allowed to participate in this review.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    files = SubmissionFile.objects.filter(submission=review.submission)
    convo = ReviewConvo.objects.filter(review=review)

    form = ReviewConvoForm()

    log_review(username, review, True)

    allow_to_score = False
    if username == review.assigned.username:
        allow_to_score = True

    return render(request, 'assignment_review.html', {
            'usertype': usertype,
            'allow_to_score': allow_to_score,
            'review': review,
            'files': files,
            'convo': convo,
            'a_name': a_name,
            'form': form,
        })

@ajax
def review_convo(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session["user"]
    usertype = request.session["usertype"]
    review = Review.objects.get(pk=id)

    allowed = False
    if review.submission.student.username == username or review.assigned.username == username:
        allowed = True

    if not allowed:
        try:
            permissions = Permission.objects.get(review=review, student__username=username)
            allowed = True
        except:
            allowed = False

    if not allowed:
        messages.info(request, 'You are not allowed to participate in this review.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    convo = ReviewConvo.objects.filter(review=review)

    form = ReviewConvoForm()

    log_review(username, review, True)

    allow_to_score = False
    if username == review.assigned.username:
        allow_to_score = True

    return render(request, 'assignment_reviewconvo.html', {
            'usertype': usertype,
            'allow_to_score': allow_to_score,
            'review': review,
            'convo': convo,
            'a_name': a_name,
            'form': form,
        })

@ajax
def review_menu(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session['user']

    # TODO Doesn't check which assignment
    log = StudentLog.objects.filter(student__username=username)
    reviews = Review.objects.filter(Q(assigned__username=username, submission__assignment__short_name=a_name) | Q(submission__student__username=username)).select_related('assigned', 'submission__student')
    convos = ReviewConvo.objects.all().select_related('review')

    log_dict = {}
    for l in log:
        log_dict[l.details] = l.created

    convos_dict = {}
    convos_count = {}
    for c in convos:
        convos_dict[c.review.pk] = c.created
        if convos_count.has_key(c.review.pk):
            convos_count[c.review.pk] += 1
        else:
            convos_count[c.review.pk] = 1

    review_assigned = set()
    review_submission = set()
    review_permission = set()

    #convo_new = "<img src=\"https://s3.amazonaws.com/static-style/dist/green_dot.png\">"
    convo_new = ""

    def get_review_details(r):
        r.end = ""
        if convos_count.has_key(r.pk):
            r.end += "<span class=\"badge pull-right\">" + str(convos_count[r.pk]) + "</span>"

        log_key = "review_" + str(r.pk)
        if log_dict.has_key(log_key):
            if convos_dict.has_key(r.pk):
                if log_dict[log_key] < convos_dict[r.pk]:
                    r.end += convo_new
        else:
            r.end += convo_new

        return r

    for r in reviews:
        if r.assigned.username == username:
            review_assigned.add(get_review_details(r))

        elif r.submission.student.username == request.session['user']:
            review_submission.add(get_review_details(r))

    review_permissions = set()
    try:
        permissions = Permission.objects.filter(student__username=username, review__submission__assignment__short_name=a_name).prefetch_related('review', 'review__submission__student')
        for p in permissions:
            review_permissions.add(get_review_details(p.review))
    except:
        permissions = Permission.objects.none()

    return render(request, 'assignment_reviewmenu.html', {
        'review_assigned': review_assigned,
        'review_submission': review_submission,
        'review_permissions': review_permissions,
        'a_name': a_name,
    })

@ajax
def submission(request, a_name):
    username = request.session["user"]
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)

    form = ReportForm()

    try:
        submission = Submission.objects.get(student__username=username, assignment__short_name=a_name)
        files = SubmissionFile.objects.filter(submission=submission)
    except:
        submission = Submission.objects.none()
        files = SubmissionFile.objects.none()

    return render(request, 'assignment_submitreport.html', {
            'ap': ap,
            'a_name': a_name,
            'username': username,
            'submission': submission,
            'files': files,
            'form': form,
        })

@ajax
def submission_files(request, a_name, username):
    files = SubmissionFile.objects.filter(submission__student__username=username, submission__assignment__short_name=a_name)

    return render(request, 'assignment_submission_files.html', {
            'a_name': a_name,
            'username': username,
            'files': files,
    })

@ajax
def submission_add(request, a_name):
    username = request.session["user"]
    try:
        submission = Submission.objects.get(student__username=username, assignment__short_name=a_name)
    except:
        s = Student.objects.get(username=username)
        a = Assignment.objects.get(short_name=a_name)
        submission = Submission()
        submission.student = s
        submission.assignment = a
        submission.save()

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            file = SubmissionFile()
            file.name = form.cleaned_data['file_name']
            file.link = form.cleaned_data['file_link']
            print file.name
            print file.link
            file.submission = submission
            file.save()
            messages.success(request, "File was added successfully.")
        else:
            messages.warning(request, "Failed to add file.")

@ajax
def submission_delete(request, a_name, id):
    response = {}
    username = request.session["user"]
    file = SubmissionFile.objects.get(pk=id)
    if file.submission.student.username == username:
        file.delete()
        messages.success(request, "File was deleted successfully.")
        response['result'] = "success"
    else:
        messages.warning(request, "Login to delete file.")
        response['result'] = "fail"
    return HttpResponse(json.dumps(response), content_type="application/json")

def submit_reviewscore(request, a_name, review_id, value):
    try:
        review = Review.objects.get(pk=review_id)
        review.score = value
        review.save()
        messages.success(request, "Changed score to %s" % str(value))
    except:
        messages.warning(request, "Couldn't find the review. Something went wrong!")

    return HttpResponseRedirect(reverse('assignment:review', args=[a_name, review_id]))

@ajax
def submit_reviewconvo(request, a_name, id):
    s = Student.objects.get(username=request.session['user'])

    if request.method == 'POST':
        form = ReviewConvoForm(request.POST)
        if form.is_valid():
            review = Review.objects.get(pk=id)
            convo = ReviewConvo()
            convo.review = review
            convo.student = s
            convo.text = form.cleaned_data['text']
            print convo.text
            convo.score = "0.0"
            convo.save()
            messages.success(request, "Review comment entered successfully.")
        else:
            messages.warning(request, "Review comment was not saved. Contact system admin.")

@ajax
def delete_reviewconvo(request, a_name, id):
    if request.method == 'POST':
        convo = ReviewConvo.objects.get(pk=id)
        convo.delete()
        messages.success(request, "Review comment was deleted.")
    else:
        messages.warning(request, "Review comment cannot be deleted.")
