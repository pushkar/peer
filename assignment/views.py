import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils import timezone
from assignment.models import Assignment, AssignmentPage
from assignment.utils import localize_timedelta, force_logout
import assignment.iosolutions as iosolutions
from student.models import Student
import student.banish as banish
import student.utils as utils
from django_ajax.decorators import ajax

log = logging.getLogger(__name__)

def get_assignments_data(username, a_name=None, p_name=None):
    data = {}
    student = Student.objects.get(username=username)
    assignments = Assignment.objects.all()
    data['student'] = student
    data['assignments'] = assignments
    if a_name:
        assignment = assignments.filter(short_name=a_name)
        pages = AssignmentPage.objects.filter(assignment__short_name=a_name)
        data['a'] = assignment
        data['pages'] = pages
        if p_name:
            data['page_this'] = pages.filter(name=p_name)
    return data

# Displays all Assignments
def index(request):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    return render(request, 'assignment_index.html', {
        **get_assignments_data(request.session['user']),
        })

# Default view for assignments
def home(request, a_name):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    extra_scripts = ""
    if request.method == "GET":
        if 'page' in request.GET:
            p_name = request.GET['page']
            extra_scripts = "load_div(\'"+ reverse('assignment:page', args=[a_name, p_name]) +"\', \'#assignment_content\'); \n"

        if 'code' in request.GET:
            a_name = request.GET['code']
            extra_scripts = "load_div(\'"+ reverse('assignment:code', args=[a_name]) +"\', \'#assignment_content\'); \n"

    return render(request, 'assignment_pagebase.html', {
        **get_assignments_data(request.session['user'], a_name),
        'extra_scripts': extra_scripts,
    })

# Displays a page from the database
@ajax
def page(request, a_name, p_name):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    return render(request, 'assignment_pageview.html', {
        **get_assignments_data(request.session['user'], a_name, p_name),
        })

@ajax
def code(request, a_name):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    data = get_assignments_data(request.session['user'], a_name)
    s = data['student']
    a = data['a'][0]

    deadline = a.due_date
    endline = deadline
    submit_late = False
    time_left = ""
    if a.end_date:
        endline = a.end_date
    if deadline > timezone.now():
        tl = deadline - timezone.now()
        time_left = "(%s left)" % localize_timedelta(tl)
    elif timezone.now() < endline:
        tl = endline - timezone.now()
        submit_late = True
        time_left = "(%s left)" % localize_timedelta(tl)
    else:
        time_left = "(Deadline Passed)"

    solutions = iosolutions.get(s, a, 10)
    stats = iosolutions.get_stats(solutions)

    return render(request, 'codework_work.html', {
        **data,
        'solutions': solutions,
        'deadline': deadline,
        'time_left': time_left,
        'submit_late': submit_late,
        'stats': stats,
        })

@ajax
def update(request, id):
    if not utils.check_session(request):
        return HttpResponseRedirect(reverse('student:index'))

    s = Student.objects.get(username=request.session['user'])
    if banish.banish_check(request, s):
        force_logout(request)

    output_submitted = ""
    if request.method == "POST":
        output_submitted = request.POST.get("output", "")
        submit_late = request.POST.get("submit_late", "")
        solution = iosolutions.get_by_id(id)
        if len(solution) > 1:
            messages.error(request, "More than one solution found. Error!")
        else:
            ret = iosolutions.update(solution, output_submitted, submit_late)
            iosolutions.check(solution)
            messages.success(request, ret)
