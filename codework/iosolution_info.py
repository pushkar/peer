from django.contrib import messages
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

def solution_get(s, a, n):
    solution_len = IOSolution.objects.filter(student=s, assignment=a).count()
    pairs_needed = 0
    if solution_len < n:
        pairs_needed = n-solution_len

    for i in range(0, pairs_needed):
        pair = pair_get_random(a)
        IOSolution.objects.get_or_create(student=s, assignment=a, pair=pair)

    return IOSolution.objects.filter(student=s, assignment=a)

def solution_update(pk, output=None, comments=None):
    pair = IOSolution.objects.get(pk=pk)
    pair.output_submitted = output
    pair.comments = comments
    pair.save()

    if is_number(output):
        if math.fabs(float(output) - float(pair.pair.output)) < 0.01:
            return "Answer is correct."
        else:
            return "Answer is wrong."
    else:
        return "Answer is not a number."
