from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from assignment.models import *
from student.models import *
from student.log import *

from django.contrib.auth.forms import AuthenticationForm
from django_ajax.decorators import ajax

from student.students_info import *
from submission_info import *
from submissions_info import *
from review_info import *
from reviews_info import *
from review_convo_info import *
from review_convos_info import *

import re
import numpy as np
import csv
import json
import random

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
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)
    ap = AssignmentPage.objects.filter(assignment=a)
    ap_this = ap.filter(name=p_name)

    return render(request, 'assignment_pageview.html', {
            'student': s,
            'a': a,
            'assignments': a_all,
            'ap': ap,
            'ap_this': ap_this,
            'a_name': a_name,
        })

def find_reviewers(request, a_name, submission_id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])

    sub_info = submission_info()
    submission = sub_info.get_by_id(submission_id)

    if s != submission.student:
        messages.error(request, "You are not allowed to request reviewers")
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))


    if sub_info.assign_reviewers(submission) == True:
        messages.success(request, sub_info.get_message())
    else:
        messages.warning(request, sub_info.get_message())

    return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

def find_reviews(request, a_name, submission_id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a = Assignment.objects.get(short_name=a_name)

    sub_info = submission_info()

    if sub_info.assign_submissions(a, s) == True:
        messages.success(request, sub_info.get_message())
    else:
        messages.warning(request, sub_info.get_message())

    return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

@ajax
def stats(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)

    convos = ReviewConvo.objects.filter(review__submission__assignment__short_name=a_name)
    submission_count = Submission.objects.filter(assignment__short_name=a_name).count()
    convos_count = len(convos)

    r_info = reviews_info()
    r_info.get_reviews_by_assignment_and_usertype(a, "ta")
    stats = r_info.get_stats()

    display = False
    if stats['completed'] > 95:
        display = True

    return render(request, 'assignment_stats.html', {
            'student': s,
            'a_name': a_name,
            'a': a,
            'submission_count': submission_count,
            'convos_count': convos_count,
            'stats': stats,
            'display': display,
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
            if p_name != "":
                if p_name == "stats":
                    extra_scripts = "load_div(\'"+ reverse('assignment:stats', args=[a_name]) +"\', \'#assignment_content\'); \n"
                elif p_name == "admin":
                    action = request.GET.get('action', 'stats')
                    if action == "stats":
                        extra_scripts = "load_div(\'"+ reverse('assignment:admin_stats', args=[a_name]) +"\', \'#assignment_content\'); \n"
                    elif action == "superman":
                        extra_scripts = "load_div(\'"+ reverse('assignment:admin', args=[a_name]) +"\', \'#assignment_content\'); \n"
                    else:
                        order_by = request.GET.get('order_by', 'assigned')
                        extra_scripts = "load_div(\'"+ reverse('assignment:admin_reviews', args=[a_name, action, order_by]) +"\', \'#assignment_content\'); \n"
                else:
                    extra_scripts = "load_div(\'"+ reverse('assignment:page', args=[a_name, p_name]) +"\', \'#assignment_content\'); \n"

        if request.GET.has_key('review'):
            review_pk = request.GET['review']
            extra_scripts = "load_div(\'"+ reverse('assignment:review', args=[a_name, review_pk]) +"\', \'#assignment_content\'); \n"

        if request.GET.has_key('code'):
            a_name = request.GET['code']
            extra_scripts = "load_div(\'"+ reverse('codework:work', args=[a_name]) +"\', \'#assignment_content\'); \n"

    s = Student.objects.get(username=request.session['user'])
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)
    ap = AssignmentPage.objects.filter(assignment__short_name=a_name)

    sub_info = submission_info()
    submission = sub_info.get_by_student_and_assignment(s, a)
    if submission:
        submission.files = sub_info.get_files(submission)

    return render(request, 'assignment_pagebase.html', {
        'student': s,
        'a': a,
        'assignments': a_all,
        'ap': ap,
        'a_name': a_name,
        'submission': submission,
        'extra_scripts': extra_scripts,
    })

@ajax
def admin(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)

    message = "<br />"
    if s.usertype == "student":
        messages.info(request, 'You are not allowed to use the Admin section.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    if 'assign' in request.GET:
        sub_info = submissions_info()
        sub_info.get_submissions_by_assignment(a)
        submissions = sub_info.shuffle()

        r_info = reviews_info()
        r_info.get_reviews_by_assignment_and_usertype(a, "ta")
        reviews = r_info.get_reviews()

        for r in reviews:
            if r.submission in submissions:
                message += "Already assigned for " + str(r.submission) + "<br />"
                submissions.remove(r.submission)

        s_info = students_info()
        tas = s_info.get_all_tas()

        tas_count = len(tas)
        submissions_count = len(submissions)
        reviews_per_ta = np.ceil(float(submissions_count)/tas_count)
        reviews_per_ta = int(reviews_per_ta)

        message += "Number of submissions: " + str(submissions_count) + "<br />"
        message += "Number of TAs: " + str(tas_count) + "<br />"

        i = 0
        count = 0
        for s in submissions:
            Review.objects.get_or_create(submission=s, assigned=tas[i])
            message += "Assigned " + str(s) + " to " + str(tas[i]) + "<br />"
            if count >= reviews_per_ta:
                count = 0
                i = i + 1
            count = count + 1

    return render(request, 'assignment_admin.html', {
        'student': s,
        'a': a,
        'assignments': a_all,
        'a_name': a_name,
        'message': message,
    })

@ajax
def admin_stats(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)

    if s.usertype == "student":
        messages.info(request, 'You are not allowed to use the Admin section.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    tas_stats = {}
    tas = Student.objects.filter(usertype="ta")

    reviews = reviews_info()
    reviews.get_reviews_by_assignment(a)

    for ta in tas:
        tas_stats[ta.username] = {}
        ta_dict = {}
        ta_dict['lastname'] = ta.lastname
        ta_dict['firstname'] = ta.firstname
        ta_dict['username'] = ta.username
        tas_stats[ta.username]['user'] = ta_dict
        reviews_ta = reviews.filter_by_assigned(ta)
        stats_ta = reviews.get_stats(reviews_ta)
        tas_stats[ta.username]['stats'] = stats_ta

    return render(request, 'assignment_admin_stats.html', {
        'student': s,
        'a': a,
        'assignments': a_all,
        'a_name': a_name,
        'tas_stats': tas_stats,
    })

@ajax
def admin_reviews(request, a_name, action, order_by):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    a_all = Assignment.objects.all()
    a = a_all.filter(short_name=a_name)

    if s.usertype == "student":
        messages.info(request, 'You are not allowed to use the Admin section.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    ob = order_by
    if order_by == "submission":
        order_by = "submission__student__lastname"
    elif order_by == "assigned":
        order_by = "assigned__lastname"

    reviews = reviews_info()
    if action == "ta":
        reviews.get_reviews_by_assignment_and_usertype(a, "ta", order_by)
        reviews = reviews.get_reviews()
    elif action == "me":
        reviews.get_reviews_by_assignment(a, order_by)
        reviews = reviews.filter_by_assigned(s)
    elif action == "me_all":
        reviews.get_reviews_by_assignment(a, order_by)
        reviews_all = []
        for r in reviews.filter_by_assigned(s):
            # Puting objects in the list destroys the order_by order
            reviews_all.extend(reviews.filter_by_submission(r.submission))
        reviews = reviews_all
    else:
        reviews.get_reviews_by_assignment(a, order_by)
        reviews = reviews.get_reviews()

    return render(request, 'assignment_admin_reviews.html', {
        'student': s,
        'a': a,
        'assignments': a_all,
        'a_name': a_name,
        'reviews': reviews,
        'action': action,
        'order_by': ob,
    })

@ajax
def review(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    allow_to_score = False
    score_on_hundred = False
    username = request.session["user"]
    usertype = request.session["usertype"]
    review = Review.objects.get(pk=id)

    allowed = False
    if review.submission.student.username == username or review.assigned.username == username:
        allowed = True

    if usertype == "ta" or usertype == "superta":
        allowed  = True
        allow_to_score = True

    if not allowed:
        try:
            permissions = Permission.objects.get(review=review, student__username=username)
            allowed = True
        except:
            allowed = False

    if not allowed:
        messages.info(request, 'You are not allowed to participate in this review.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    files = json.loads(review.submission.files)
    convo = ReviewConvo.objects.filter(review=review)

    form = ReviewConvoForm()

    log_review(username, review, True)

    if username == review.assigned.username:
        allow_to_score = True

    score_on_hundred = False
    if review.assigned.usertype == "ta":
        score_on_hundred = True

    ## This allows Hamid to score of 100
    if review.assigned.usertype == "superta" and review.assigned.username == username:
        score_on_hundred = True

    return render(request, 'assignment_review.html', {
            'username': username,
            'usertype': usertype,
            'allow_to_score': allow_to_score,
            'score_on_hundred': score_on_hundred,
            'review': review,
            'files': files,
            'convo': convo,
            'files': files,
            'a_name': a_name,
            'form': form,
        })

@ajax
def review_convo(request, a_name, id="1"):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session["user"]
    usertype = request.session["usertype"]
    s = Student.objects.get(username=request.session['user'])

    review = Review.objects.get(pk=id)

    allowed = False
    if review.submission.student.username == username or review.assigned.username == username:
        allowed = True

    if usertype == "ta" or usertype == "superta":
        allowed = True

    if not allowed:
        try:
            permissions = Permission.objects.get(review=review, student=s)
            allowed = True
        except:
            allowed = False

    if not allowed:
        messages.info(request, 'You are not allowed to participate in this review.')
        return HttpResponseRedirect(reverse('assignment:home', args=[a_name]))

    convo = ReviewConvo.objects.filter(review=review)
    convo_info = {}
    for c in convo:
        c_info = review_convo_info()
        c_info.set_convo(c)
        c.details = c_info.get_likes_info(s)

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
    reviews = Review.objects.filter(Q(assigned__username=username) & Q(submission__assignment__short_name=a_name) | Q(submission__student__username=username) & Q(submission__assignment__short_name=a_name)).select_related('assigned', 'submission__student')
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
        permissions = Permission.objects.filter(student__username=username).prefetch_related('review') #, review__submission__assignment__short_name=a_name).prefetch_related('review', 'review__submission__student')
        for p in permissions:
            for r in p.review.all():
                review_permissions.add(get_review_details(r))
    except:
        permissions = Permission.objects.none()

    return render(request, 'assignment_reviewmenu.html', {
        'review_assigned': review_assigned,
        'review_submission': review_submission,
        'review_permissions': review_permissions,
        'a_name': a_name,
    })

@ajax
def reviewconvo_addlike(request, a_name, review_id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session["user"])
    convo_info = review_convo_info()
    convo_info.get_convo_by_id(review_id)
    convo_info.add_like(s)

@ajax
def reviewconvo_removelike(request, a_name, review_id):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session["user"])
    convo_info = review_convo_info()
    convo_info.get_convo_by_id(review_id)
    convo_info.remove_like(s)

@ajax
def review_debug(request, a_name):
    if not check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    username = request.session["user"]

    if False:
        reviews = Review.objects.filter(submission__assignment__short_name=a_name)
        for r in reviews:
            count = ReviewConvo.objects.filter(review=r).count()
            if count == 0:
                r.delete()

    class reviews:
        submission = None
        reviews = None
        assigns = None

        def __init__(self, s, r, a):
            self.submission = s
            self.reviews = r
            self.assigns = a

    reviews_dict = {}

    students = Student.objects.all()

    for student in students:
        submission = Submission.objects.filter(assignment__short_name=a_name, student=student)
        review = Review.objects.filter(submission=submission)
        assigned = Review.objects.filter(submission__assignment__short_name=a_name, assigned=student)
        optin = OptIn.objects.filter(student=student)

        r = reviews(submission, review, assigned)
        reviews_dict[student] = r

    return render(request, 'assignment_reviewdebug.html', {
        'a_name': a_name,
        'reviews_dict': reviews_dict,
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

def submit_add_reviewscore(request, a_name, review_id, value):
    try:
        review = Review.objects.get(pk=review_id)
        if review.score == None or review.score == "":
            review.score = "0"
        score = int(review.score)
        review.score = str(score + int(value))
        review.save()
        messages.success(request, "Changed score to %s" % str(review.score))
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
