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
    review = Review.objects.filter(review_userid=request.session['student_id'])

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

    return render(request, 'recommender_submitreport.html', {
        'message': request.session['message'],
        'report_message': report_message,
        'si': si,
        'form': form,
        'review': review,
        })

def submit_review(request):
    request.session['message'] = ""

    try:
        review = Review.objects.filter(userid=request.session['student_id'])
    except:
        review = Review.objects.none()

    return render(request, 'recommender_review.html', {
        'message': request.session['message'],
        'review': review,
        })

def submit_reviewtext(request, review_pk):
    request.session['message'] = ""

    review_text_submission = False
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_text = form.cleaned_data['review_text']
            review_text_submission = True


    review = Review.objects.get(pk=review_pk)
    review_si = StudentInfo.objects.get(pk=review.review_userid)
    reviewtext = ReviewText.objects.filter(review_pk=review_pk)

    if int(review.userid) == int(request.session['student_id']):
        text_type = "Review"
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
        else:
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
    except:
        rt_last = ReviewText.objects.none()
        form = ReviewForm()


    return render(request, 'recommender_reviewtext.html', {
        'message': request.session['message'],
        'review': review,
        'review_si': review_si,
        'reviewtext': reviewtext,
        'form': form,
        'text_type': text_type,
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
