from django.contrib import messages
from django.utils import timezone
from codework.models import *
from codework.iopairs_info import *

import random
import math

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# returns True if deadline is not passed
def check_deadline(a):
    now = timezone.now()
    if a.due_date > now:
        return True
    else:
        return False

def solution_get(s, a, n):
    solution_len = IOSolution.objects.filter(student=s, assignment=a).count()
    pairs_needed = 0
    if solution_len < n:
        pairs_needed = n-solution_len

    for i in range(0, pairs_needed):
        pair = pair_get_random(a)
        IOSolution.objects.get_or_create(student=s, assignment=a, pair=pair)

    return IOSolution.objects.filter(student=s, assignment=a)

def solution_check(s, a):
    solutions = IOSolution.objects.filter(student=s, assignment=a)
    solution_check_ = {}
    for s in solutions:
        if s.output_submitted:
            if is_number(s.output_submitted):
                if math.fabs(float(s.output_submitted) - float(s.pair.output)) < 0.01:
                    solution_check_[s.pk] = "Answer is correct."
                else:
                    solution_check_[s.pk] = "Answer is wrong."
            else:
                solution_check_[s.pk] = "Answer is not a number."
        else:
            solution_check_[s.pk] = "No solution yet."
    return solution_check_


def solution_update(pk, output=None, comments=None):
    ret = ""
    pair = IOSolution.objects.get(pk=pk)
    if check_deadline(pair.assignment):
        pair.output_submitted = output
        pair.comments = comments
        pair.save()
    else:
        ret += "Deadline has passed. Answer will not be recorded. "


    if is_number(output):
        if math.fabs(float(output) - float(pair.pair.output)) < 0.01:
            ret += "Answer is correct."
        else:
            ret += "Answer is wrong."
    else:
        ret += "Answer is not a number."
    return ret
