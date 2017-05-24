import random
import json
import logging
import assignment.hw_check as hw_check
import assignment.iopairs as iopairs
from assignment.models import Assignment, IOPair, IOSolution
from django.contrib import messages
from django.utils import timezone
from django.forms.models import model_to_dict

log = logging.getLogger(__name__)

def check_deadline(a):
    ''' Checks if the deadline has passed or not
        :returns: True if deadline is not passed
    '''
    now = timezone.now()
    if a.due_date > now:
        return True
    else:
        return False

def get(s, a, n):
    ''' Generates an IO pair for a student
        For each student s and assignment a, create n examples of IO pairs.
        :param s: Student
        :param a: assignment
        :param m: int, number of pairs
        :returns: List of IOSolutions generated
    '''
    solutions = IOSolution.objects.filter(student=s, assignment=a).count()
    if solutions == n:
        return IOSolution.objects.filter(student=s, assignment=a)

    iopairs_count = len(iopairs.get(a))
    if iopairs_count < n:
        n = iopairs_count

    log.info("%s Generating %s iopairs" % (s, n))
    pairs = iopairs.get_random(a, n)
    for pair in pairs:
        ios = IOSolution.objects.get_or_create(student=s, assignment=a, pair=pair)
        log.info("Created IOSolution %s" % ios[0])

    return IOSolution.objects.filter(student=s, assignment=a)

def get_by_student(s, solutions=None):
    ''' Filters IOSolution objects for student s
        :param s: Student
        :returns: List of IOSolutions generated
    '''
    if solutions:
        return solutions.filter(student=s)

    return IOSolution.objects.filter(student=s)

def get_by_assignment(a, solutions=None):
    ''' Filters IOSolution objects for assignment a
        :param s: Student
        :returns: List of IOSolutions generated
    '''
    if solutions:
        return solutions.filter(assignment=a)

    return IOSolution.objects.filter(assignment=a)

def get_none():
    return IOSolution.objects.none()

def get_by(s, a):
    return IOSolution.objects.filter(student=s, assignment=a)

def get_by_id(pk):
    solution = IOSolution.objects.filter(pk=pk)
    if len(solution) > 1:
        log.error("Found more than 1 solution")
    return solution

def update(solution, output=None, submit_late="false"):
    try:
        solution = solution[0]
        if check_deadline(solution.assignment) or submit_late == "true":
            if output:
                if len(output) > 100000:
                    return "Solution length should be less than 100,000 chars."
                solution.output_submitted = output
            solution.save()
            return "Solution submitted."
        else:
            return "Deadline has passed. Answer will not be recorded."
    except Exception as e:
        return "Exception: %s" % (e)

def check(solutions):
    for s in solutions:
        a_name = s.assignment.short_name
        if a_name == "hw1":
            hw_check.check_hw1(s)
        elif a_name == "hw2":
            hw_check.check_hw2(s)
        elif a_name == "hw3":
            hw_check.check_hw4(s)
        elif a_name == "hw4":
            hw_check.check_hw4(s) # Needs to change later
        elif a_name == "hw5":
            hw_check.check_hw7(s)
        elif a_name == "hw6":
            hw_check.check_hw6(s)
        elif a_name == "hw7":
            hw_check.check_hw7(s)
        elif a_name == "hw8":
            hw_check.check_hw8(s)

def get_stats(solutions):
    stats = {}
    stats['total'] = 0.0
    for s in solutions:
        stats['total'] += float(s.score)
    return stats
