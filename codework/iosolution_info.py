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
                return "Answer is wrong. ("+ output_submitted +")"
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

def check_hw5(output, output_submitted):
    try:
        if output_submitted:
            output = output.strip('{}()[]')
            output_submitted = output_submitted.strip('{}()[]')
            output = output.strip().split(',')
            output_submitted = output_submitted.strip().split(',')
            if len(output) == len(output_submitted):
                i = 1
                err = []
                for (o, os) in zip(output, output_submitted):
                    if math.fabs(float(o) - float(os)) > 0.01:
                        err.append(i)
                    i = i + 1
                if len(err) == 0:
                    return "Solution is correct."
                else:
                    if len(err) == 1:
                        return "Value at state " + str(err[-1]) + " is wrong. You are close!"
                    return "Values at states " + " ".join(str(x)+", " for x in err[:-1]) + str(err[-1]) + " are wrong."

            else:
                return "The problem has " + str(len(output)) + " states, but your submission has " + str(len(output_submitted)) + " states."
        else:
            return "No solution yet."
    except Exception as e:
        return '%s (%s)' % (e.message, type(e))

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
            elif a_name == "hw5":
                ret[s.pk] = check_hw5(s.pair.output, s.output_submitted)
        return ret


def solution_update(pk, output=None, submit_late="false", comments=None):
    ret = ""
    solution = IOSolution.objects.get(pk=pk)
    if check_deadline(solution.assignment) or submit_late=="true":
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
    elif a_name == "hw5":
        ret += check_hw5(solution.pair.output, solution.output_submitted)
    return ret
