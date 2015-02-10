from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
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

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)
    ap = AssignmentPage.objects.filter(assignment=a)

    try:
        submission = Submission.objects.filter(assignment=a, student=s)
    except:
        submission = Submission.objects.none()

    # TODO Doesn't check which assignment
    try:
        review_assigned = Review.objects.filter(assigned=s)
        for r in review_assigned:
            c = log_isread(s, r)
            if c > 0:
                r.read = "("+ str(c) +")"
            elif c == -1:
                r.read = "(New)"

    except:
        review_assigned = Review.objects.none()

    try:
        review_submission = Review.objects.filter(submission=submission)
        for r in review_submission:
            c = log_isread(s, r)
            if c > 0:
                r.read = "("+ str(c) +")"
            elif c == -1:
                r.read = "(New)"
    except:
        review_submission = Review.objects.none()

    try:
        permissions = Permission.objects.filter(student=s)
        for p in permissions:
            c = log_isread(s, p.review)
            if c > 0:
                p.review.read = "("+ str(c) +")"
            elif c == -1:
                p.review.read = "(New)"
    except:
        permissions = Permission.objects.none()

    return render(request, 'assignment_homeview.html', {
            'student': s,
            'submission': submission,
            'review_assigned': review_assigned,
            'review_submission': review_submission,
            'permissions': permissions,
            'assignment': a,
            'ap': ap,
            'a_name': a_name,
        })

def review(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)
    ap = AssignmentPage.objects.filter(assignment=a)


    review = Review.objects.get(pk=id)

    allowed = False
    if s.pk == review.submission.student.pk or s.pk == review.assigned.pk:
        allowed = True

    if not allowed:
        try:
            permissions = Permission.objects.get(review=review, student__pk=s.pk)
            allowed = True
        except:
            allowed = False

    if not allowed:
        messages.info(request, 'You are not allowed to participate in this review.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    files = SubmissionFile.objects.filter(submission=review.submission)
    convo = ReviewConvo.objects.filter(review=review)

    form = ReviewConvoForm()

    log_review(s, review, True)

    return render(request, 'assignment_review.html', {
            'student': s,
            'review': review,
            'files': files,
            'convo': convo,
            'assignment': a,
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
