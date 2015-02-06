from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from assignment.models import *
from student.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import re
import numpy as np
import csv

def check_session(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    request.session['message'] = ""

    if not 'user' in request.session:
        request.session['message'] = ""
        request.session['user'] = ""

    if not request.session['user']:
        return False
    return True


def index(request):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.all()

    return render(request, 'assignment_index.html', {
            'message': request.session['message'],
            'student': s,
            'assignments': a,
        })

def assignment_page(request, a_name, p_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(username=request.session['user'])
    ap = AssignmentPage.objects.filter(assignment__assignment_name=a_name)
    ap_this = ap.filter(page_name=p_name)

    return render(request, 'assignment_pageview.html', {
            'message': request.session['message'],
            'student': s,
            'assignmentpages': ap,
            'ap_this': ap_this,
        })

# Default view for assignments
# Enlists tasks
def assignment_view(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(username=request.session['user'])
    ap = AssignmentPage.objects.filter(assignment__assignment_name=a_name)

    try:
        review = Review.objects.filter(review_userid=s.pk)
    except:
        review = Review.objects.none()
    return render(request, 'assignment_taskview.html', {
            'message': request.session['message'],
            'student': s,
            'assignmentpages': ap,
            'review': review,
        })

def submit_report(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(username=request.session['user'])
    ap = AssignmentPage.objects.filter(assignment__assignment_name=a_name)

    report_message = "None."

    try:
        sub = Submission.objects.get(student__userid=s.userid, assignment__assignment_name=a_name)
    except:
        sub = Submission()
        sub.user_pk = request.session['student_id']
        sub.assignment_name = a_name
        sub.score = "0.0"

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            sub.report = form.cleaned_data['report_link']
            sub.save()
            request.session['message'] = "Report at " + sub.report + " accepted."
        else:
            request.session['message'] = "Something went wrong during submission."
    else:
        form = ReportForm()

    if sub.report:
        if len(sub.report) > 0:
            report_message = sub.report

    return render(request, 'assignment_submitreport.html', {
        'message': request.session['message'],
        'form': form,
        'student': s,
        'assignmentpages': ap,
        'report_message': report_message,
        })

def submit_review(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    try:
        review = Review.objects.filter(userid=request.session['student_id'])
    except:
        review = Review.objects.none()

    s = Student.objects.get(pk=request.session['student_id'])
    a = Assignment.objects.filter(assignment_name=a_name)
    ap = AssignmentPage.objects.filter(assignment_name=a_name)

    return render(request, 'assignment_review.html', {
        'message': request.session['message'],
        'student': s,
        'review': review,
        'assignment': a,
        'assignmentpages': ap,
        })

def submit_reviewscore(request, a_name, review_pk):
    if request.method == 'POST':
        form_score = ScoreForm(request.POST)
        if form_score.is_valid():
            review = Review.objects.get(pk=review_pk)
            review.review_score = form_score.cleaned_data['review_score']
            review.save()
    return submit_reviewtext(request, review_pk)

def submit_reviewtext(request, a_name, review_pk):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(pk=request.session['student_id'])
    a = Assignment.objects.filter(assignment_name=a_name)
    ap = AssignmentPage.objects.filter(assignment_name=a_name)

    review_text_submission = False
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_text = form.cleaned_data['review_text']
            review_text_submission = True

    try:
        sub = Submission.objects.get(user_pk=s.id, assignment_name=a_name)
    except:
        sub = Submission.ojects.none()

    try:
        review = Review.objects.get(pk=review_pk)
        review_si = StudentInfo.objects.get(pk=review.review_userid)
        reviewtext = ReviewText.objects.filter(review_pk=review_pk)
    except:
        return HttpResponseRedirect('/assignment/review')

    form_score = None
    if int(review.review_userid) == int(request.session['student_id']):
        text_type = "Review"
        data = {'review_score': review.review_score}
        form_score = ScoreForm(initial=data)
    else:
        text_type = "Rebuttal"

    try:
        rt_last = reviewtext.order_by('-created')[0]

        if int(rt_last.userid) == int(request.session['student_id']):
            if review_text_submission == True:
                rt_last.review_text = review_text
                rt_last.save()
                request.session['message'] += text_type + " updated."
            data = {'review_text': rt_last.review_text}
            form = ReviewForm(initial=data)
        elif int(rt_last.review_userid) == int(request.session['student_id']):
            if review_text_submission == True:
                rt_last.review_text = review_text
                rt_last.save()
                request.session['message'] += text_type + " updated."
            data = {'review_text': rt_last.review_text}
            form = ReviewForm(initial=data)
        else:
            form = ReviewForm()
    except:
        rt_last = ReviewText.objects.none()
        if review_text_submission == True:
            r = ReviewText()
            r.userid = request.session['student_id']
            r.review_pk = review_pk
            r.review_text = review_text
            r.save()
            request.session['message'] += text_type + " added."
            data = {'review_text': review_text}
            form = ReviewForm(initial=data)
            reviewtext = ReviewText.objects.filter(review_pk=review_pk)
        else:
            form = ReviewForm()

    return render(request, 'assignment_reviewtext.html', {
        'message': request.session['message'],
        'review': review,
        'review_si': review_si,
        'reviewtext': reviewtext,
        'form': form,
        'form_score': form_score,
        'text_type': text_type,
        'student': s,
        'assignment': a,
        'assignmentpages': ap,
        'submission': sub,
    })

@login_required
def adminview(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student.views.index'))

    s = Student.objects.get(pk=request.session['student_id'])
    a = Assignment.objects.filter(assignment_name=a_name)
    ap = AssignmentPage.objects.filter(assignment_name=a_name)

    return render(request, 'assignment_admin.html', {
            'message': request.session['message'],
            'student': s,
            'assignment': a,
            'assignmentpages': ap,
        })
