from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from recommender.models import *
from student.models import *

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse

import re
import numpy as np
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
    request.session['message'] = ""
    s = Student.objects.get(pk=request.session['student_id'])
    return render(request, 'recommender_overview.html', {
        'message': request.session['message'],
        'student': s,
    })

def dataset(request):
    request.session['message'] = ""
    s = Student.objects.get(pk=request.session['student_id'])
    return render(request, 'recommender_dataset.html', {
        'message': request.session['message'],
        'student': s,
    })

def leaderboard(request):
    request.session['message'] = ""
    s = Student.objects.get(pk=request.session['student_id'])
    si = StudentInfo.objects.filter(score__gt=0).order_by('score')
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
            test = np.full((1000, 1700), -1, dtype=np.int)
            test_u = np.full((1000, 1700), -1, dtype=np.int)

            with open('u_a.test', 'rb') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    if len(row) == 3:
                        test[int(row[0])][int(row[1])] = int(row[2])

            tuples = re.split(r'\n+', form.cleaned_data['test_data'])
            for row in tuples:
                n = re.split(r',+', row)
                if len(n) == 3:
                    test_u[int(n[0])][int(n[1])] = int(n[2])

            score = 0.0
            count = 0.0
            for i in range(1, 1000):
                for j in range(1, 1700):
                    if test[i][j] != -1:
                        count = count + 1.0
                        if test_u[i][j] != -1:
                            score += (test[i][j]*test[i][j] - test_u[i][j]*test_u[i][j])
                        else:
                            score += 25

            si.score = round(0.2*np.sqrt(score/count), 4)
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

    if si.report:
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

def submit_reviewscore(request, review_pk):
    if request.method == 'POST':
        form_score = ScoreForm(request.POST)
        if form_score.is_valid():
            review = Review.objects.get(pk=review_pk)
            review.review_score = form_score.cleaned_data['review_score']
            review.save()
    return submit_reviewtext(request, review_pk)

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

    form_score = None
    if int(review.userid) == int(request.session['student_id']):
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
        'form_score': form_score,
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
