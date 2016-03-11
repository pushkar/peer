from django.contrib import messages
from django.utils import timezone
from codework.models import *
from codework.iopairs_info import *

import random
import math
import re
import json

def is_number(s):
    '''
    Checks if the input is a number or not
    :returns: True if the input is a number, False otherwise.
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False

def check_hw1(s):
    output = s.pair.output
    if s.output_submitted:
        if is_number(s.output_submitted):
            if math.fabs(float(s.output_submitted) - float(output)) < 0.01:
                s.comments = "Answer is correct."
                if s.updated < s.assignment.due_date:
                    s.score = "10.0"
                else:
                    s.score = "5.0"
            else:
                s.comments = "Answer is wrong. ("+ s.output_submitted +")"
        else:
            s.comments = "Answer is not a number."
    else:
        s.comments = "No solution yet."
    s.save()

def check_hw2(s):
    return check_hw1(s)

def check_hw3(s):
    output = s.pair.output
    if s.output_submitted:
        nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
        o = re.findall(nums, output)
        o_s = re.findall(nums, s.output_submitted)
        if len(o) != 3:
            s.comments = "Input is wrong. Send the input to TA."
        if len(o_s) != 3:
            s.comments = "You need to give atleast 3 numbers: bestX=1,bestY=2,LInfinityDistance=3."

        if int(o[2]) == int(o_s[2]):
            s.comments = "LInfinityDistance Value is correct."
            if s.updated < s.assignment.due_date:
                s.score = "10.0"
            else:
                s.score = "5.0"
        else:
            s.comments = "LInfinityDistance of " + str(o_s[2]) + " is wrong. Try again."
    else:
        s.comments = "No solution yet."
    s.save()

def check_hw4(s):
    if s.output_submitted:
        try:
            json_object = json.loads(s.output_submitted)
            s.comments = "String is a valid JSON. We will validate the answer soon."
        except ValueError, e:
            s.comments = "String is not a valid JSON."
        finally:
            s.save()
    else:
        s.comments = "No solution yet."
    s.save()

def check_hw5(s):
    output = s.pair.output
    try:
        if s.output_submitted:
            output = output.strip('{}()[]')
            output_submitted = s.output_submitted.strip('{}()[]')
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
                    s.comments = "Solution is correct."
                    if s.updated < s.assignment.due_date:
                        s.score = "30.0"
                    else:
                        s.score = "15.0"
                else:
                    if len(err) == 1:
                        s.comments = "Value at state " + str(err[-1]) + " is wrong. You are close!"
                    s.comments = "Values at states " + " ".join(str(x)+", " for x in err[:-1]) + str(err[-1]) + " are wrong."

            else:
                s.comments = "The problem has " + str(len(output)) + " states, but your submission has " + str(len(output_submitted)) + " states."
        else:
            s.comments = "No solution yet."
    except Exception as e:
        s.comments = '%s (%s)' % (e.message, type(e))
    finally:
        s.save()

def check_deadline(a):
    '''
    Checks if the deadline has passed or not
    :returns: True if deadline is not passed
    '''
    now = timezone.now()
    if a.due_date > now:
        return True
    else:
        return False

class iosolution_info():
    ''' Manipulate Input/Output pairs submited by students '''
    solutions = IOPair.objects.none()

    def generate(self, s, a, n):
        ''' Generates an IO pair for a student
        For each student s and assignment a, create n examples of IO pairs.
        :param s: Student
        :param a: assignment
        :param m: int, number of pairs
        :returns: List of IOSolutions generated
        '''
        solution_len = IOSolution.objects.filter(student=s, assignment=a).count()
        pairs_needed = 0
        if solution_len < n:
            pairs_needed = n-solution_len

        for i in range(0, pairs_needed):
            pair = pair_get_random(a)
            IOSolution.objects.get_or_create(student=s, assignment=a, pair=pair)
        self.solutions = IOSolution.objects.filter(student=s, assignment=a)

    def get(self, s=None, a=None):
        ''' Gets an IOSolution
        :param s: Student
        :param a: Asssignment
        :returns: List of IOSolutions generated
        '''
        if not s and not a:
            self.solutions = IOSolution.objects.all()
        elif s and not a:
            self.solutions = IOSolution.objects.filter(student=s)
        elif a and not s:
            self.solutions = IOSolution.objects.filter(assignment=a)
        else:
            self.solutions = IOSolution.objects.filter(student=s, assignment=a)
        return self.solutions

    def update(self, pk, output=None, submit_late="false"):
        try:
            self.solutions = IOSolution.objects.filter(pk=pk)
            if len(self.solutions) == 1:
                if check_deadline(self.solutions[0].assignment) or submit_late=="true":
                    self.solutions[0].output_submitted = output
                    self.solutions[0].save()
                    return "Solution submitted."
                else:
                    return "Deadline has passed. Answer will not be recorded."
            else:
                return "Something went wrong. Only one submission allowed at a time."
        except Exception as e:
            return "%s (%s)" % (e.message, type(e))

    def get_solutions(self):
        ''' Returns IOSolutions generated in the last call '''
        return self.solutions

    def check(self):
        for s in self.solutions:
            a_name = s.assignment.short_name
            if a_name == "hw1":
                check_hw1(s)
            elif a_name == "hw2":
                check_hw2(s)
            elif a_name == "hw3":
                check_hw3(s)
            elif a_name == "hw4":
                check_hw4(s)
            elif a_name == "hw5":
                check_hw5(s)

    def grade(self):
        for s in self.solutions:
            for field in s._meta.local_fields:
                if field.name == "updated":
                    field.auto_now = False
                elif field.name == "created":
                    field.auto_now_add = False

            a_name = s.assignment.short_name
            if a_name == "hw1":
                check_hw1(s)
            elif a_name == "hw2":
                check_hw2(s)
            elif a_name == "hw3":
                check_hw3(s)
            elif a_name == "hw4":
                check_hw4(s)
            elif a_name == "hw5":
                check_hw5(s)

            for field in s._meta.local_fields:
                if field.name == "updated":
                    field.auto_now = True
                elif field.name == "created":
                    field.auto_now_add = True

    def get_stats(self):
        stats = {}
        stats['total'] = 0.0
        for s in self.solutions:
            stats['total'] += float(s.score)
        return stats
