from django.contrib import messages
from django.utils import timezone
from codework.models import *
from codework.iopairs_info import *

import random
import math
import re
import json

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def check_hw1(output, output_submitted):
    if output_submitted:
        if is_number(output_submitted):
            if math.fabs(float(output_submitted) - float(output)) < 0.01:
                return "Answer is correct."
            else:
                return "Answer is wrong."
        else:
            return "Answer is not a number."
    else:
        return "No solution yet."

def check_hw2(output, output_submitted):
    return check_hw1(output, output_submitted)

def check_hw3(output, output_submitted):
    if output_submitted:
        nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
        o = re.findall(nums, output)
        o_s = re.findall(nums, output_submitted)
        if len(o) != 3:
            return "Input is wrong. Send the input to TA."
        if len(o_s) != 3:
            return "You need to give atleast 3 numbers: bestX=1,bestY=2,LInfinityDistance=3."

        if int(o[2]) == int(o_s[2]):
            return "LInfinityDistance Value is correct."
        else:
            return "LInfinityDistance of " + str(o_s[2]) + " is wrong. Try again."
    else:
        return "No solution yet."

def check_hw4(output, output_submitted):
    if output_submitted:
        try:
          json_object = json.loads(output_submitted)
        except ValueError, e:
          return "String is not a valid JSON."
        return "String is a valid JSON. We will validate the answer soon."
    else:
        return "No solution yet."

# returns True if deadline is not passed
def check_deadline(a):
    now = timezone.now()
    if a.due_date > now:
        return True
    else:
        return False

class iosolution_info():
    solutions = IOPair.objects.none()

    def generate(self, s, a, n):
        solution_len = IOSolution.objects.filter(student=s, assignment=a).count()
        pairs_needed = 0
        if solution_len < n:
            pairs_needed = n-solution_len

        for i in range(0, pairs_needed):
            pair = pair_get_random(a)
            IOSolution.objects.get_or_create(student=s, assignment=a, pair=pair)
        self.solutions = IOSolution.objects.filter(student=s, assignment=a)

    def get(self, s, a):
        self.solutions = IOSolution.objects.filter(student=s, assignment=a)
        return self.solutions

    def get_solutions(self):
        return self.solutions

    def check(self):
        ret = {}
        for s in self.solutions:
            a_name = s.assignment.short_name
            if a_name == "hw1":
                ret[s.pk] = check_hw1(s.pair.output, s.output_submitted)
            elif a_name == "hw2":
                ret[s.pk] = check_hw2(s.pair.output, s.output_submitted)
            elif a_name == "hw3":
                ret[s.pk] = check_hw3(s.pair.output, s.output_submitted)
            elif a_name == "hw4":
                ret[s.pk] = check_hw4(s.pair.output, s.output_submitted)
        return ret


def solution_update(pk, output=None, comments=None):
    ret = ""
    solution = IOSolution.objects.get(pk=pk)
    if check_deadline(solution.assignment):
        solution.output_submitted = output
        solution.comments = comments
        solution.save()
    else:
        ret += "Deadline has passed. Answer will not be recorded. "

    a_name = solution.assignment.short_name
    if a_name == "hw1":
        ret += check_hw1(solution.pair.output, solution.output_submitted)
    elif a_name == "hw2":
        ret += check_hw2(solution.pair.output, solution.output_submitted)
    elif a_name == "hw3":
        ret += check_hw3(solution.pair.output, solution.output_submitted)
    elif a_name == "hw4":
        ret += check_hw4(solution.pair.output, solution.output_submitted)
    return ret
