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

import re
import numpy as np
import csv

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""

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

# Default view for assignments
# Enlists tasks
def home(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session['user']
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)

    # TODO Doesn't check which assignment
    log = StudentLog.objects.filter(student__username=username)
    reviews = Review.objects.filter(Q(assigned__username=username) | Q(submission__student__username=username)).select_related('assigned', 'submission__student')
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

    convo_new = "<img src=\"https://s3.amazonaws.com/static-style/dist/green_dot.png\">"

    def get_review_details(r):
        r.end = ""
        if convos_count.has_key(r.pk):
            r.end += "<span class=\"badge\">" + str(convos_count[r.pk]) + "</span>"

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
        permissions = Permission.objects.filter(student__username=username).prefetch_related('review', 'review__submission__student')
        for p in permissions:
            review_permissions.add(get_review_details(p.review))
    except:
        permissions = Permission.objects.none()

    return render(request, 'assignment_homeview.html', {
        'review_assigned': review_assigned,
        'review_submission': review_submission,
        'review_permissions': review_permissions,
        'ap': ap,
        'a_name': a_name,
    })

def review(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session["user"]
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)
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
            'allow_to_score': allow_to_score,
            'review': review,
            'files': files,
            'convo': convo,
            'ap': ap,
            'a_name': a_name,
            'form': form,
        })

def submission(request, a_name):
    return HttpResponse("Submit Report")


def submit_reviewscore(request, a_name, review_id, value):
    try:
        review = Review.objects.get(pk=review_id)
        review.score = value
        review.save()
        messages.success(request, "Changed score to %s" % str(value))
    except:
        messages.warning(request, "Couldn't find the review. Something went wrong!")

    return HttpResponseRedirect(reverse('assignment:review', args=[a_name, review_id]))

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
            messages.success(request, "Review comment entered successfullly.")
        else:
            messages.warning(request, "Review comment was not saved. Contact system admin.")

    return HttpResponseRedirect(reverse('assignment:review', args=[a_name, str(id)]) )
