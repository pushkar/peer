from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from recommender.models import *
from student.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import numpy
import csv

def index(request):
    if not 'message' in request.session:
        request.session['message'] = ""

    if not 'student_id' in request.session:
        request.session['message'] = ""
        request.session['student_id'] = -1
        return HttpResponseRedirect('/student/')

    return HttpResponseRedirect('leaderboard')

def overview(request):
    s = Student.objects.get(pk=request.session['student_id'])
    return render(request, 'recommender_overview.html', {
        'message': request.session['message'],
        'student': s,
    })

def dataset(request):
    s = Student.objects.get(pk=request.session['student_id'])
    return render(request, 'recommender_dataset.html', {
        'message': request.session['message'],
        'student': s,
    })

def leaderboard(request):
    request.session['message'] = ""
    s = Student.objects.get(pk=request.session['student_id'])
    si = StudentInfo.objects.filter(score__gt=0).order_by('-score')
    return render(request, 'recommender_leaderboard.html', {
        'message': request.session['message'],
        'student': s,
        's_info': si,
    })

def submit_prediction(request):
    request.session['message'] = ""
    si = StudentInfo.objects.get(pk=request.session['student_id'])

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            si.score = form.cleaned_data['test_data']
            si.save()
            request.session['message'] = "New score is " + str(si.score)
        else:
            request.session['message'] = "Something went wrong."
    else:
        form = PredictionForm()

    return render(request, 'recommender_submitprediction.html', {
        'message': request.session['message'],
        'si': si,
        'form': form,
        })


def submit_report(request):
    request.session['message'] = ""

    report_message = "None"
    si = StudentInfo.objects.get(pk=request.session['student_id'])
    if len(si.report) > 0:
        report_message = si.report

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            si.report = form.cleaned_data['report_link']
            si.save()
            request.session['message'] = "Report at " + si.report + " accepted."
        else:
            request.session['message'] = "Something went wrong during submission."
    else:
        form = ReportForm()

    try:
        reviews = Review.objects.filter(review_userid=request.session['student_id'])
    except:
        reviews = Review.objects.none()

    return render(request, 'recommender_submitreport.html', {
        'message': request.session['message'],
        'report_message': report_message,
        'si': si,
        'form': form,
        'reviews': reviews,
        })

def submit_review(request):
    request.session['message'] = ""

    if request.method == 'POST':
        if not 'review_pk' in request.session:
            request.session['message'] = "Something went wrong while submitting your review."
            pass
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = Review.objects.get(pk=request.session['review_pk'])
            review.text = form.cleaned_data['review_text']
            review.save()
            request.session['message'] = "Your review was saved. Thank you!"
        else:
            request.session['message'] = "Something went wrong while saving your review."

    try:
        review = Review.objects.filter(userid=request.session['student_id'])[0]
        # only a single review request per student
        review_si = StudentInfo.objects.get(pk=review.review_userid)
        data = {'review_text': review.text}
        form = ReviewForm(initial=data)
        request.session['review_pk'] = review.pk
    except:
        review = Review.objects.none()
        review_si = StudentInfo.objects.none()
        form = ReviewForm()

    return render(request, 'recommender_review.html', {
        'message': request.session['message'],
        'review': review,
        'review_si': review_si,
        'form': form,
        })

def populate(request):
    return HttpResponse("Skipped")
    students = Student.objects.all()
    for s in students:
        si = StudentInfo()
        si.pk = s.pk
        si.userid = s.userid
        si.score = 0
        si.save()
    return HttpResponse("Done")
