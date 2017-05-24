from django.contrib import messages
from django.utils import timezone
from codework.models import *
from codework.iopairs_info import *
from django.forms.models import model_to_dict

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
    output = s.pair.output
    if s.output_submitted:
        if is_number(s.output_submitted):
            if math.fabs(float(s.output_submitted) - float(output)) < 0.01:
                s.comments = "Answer is correct."
                if s.updated < s.assignment.due_date:
                    s.score = "20.0"
                else:
                    s.score = "10.0"
            else:
                s.comments = "Answer is wrong. ("+ s.output_submitted +")"
        else:
            s.comments = "Answer is not a number."
    else:
        s.comments = "No solution yet."
    s.save()

def check_hw3(s):
    output = s.pair.output
    if s.output_submitted:
        nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
        o = re.findall(nums, output)
        o_s = re.findall(nums, s.output_submitted)
        if len(o) != 3:
            s.comments = "Input is wrong. Send the input to TA."
            s.score = "0.0"
            s.save()
            return
        if len(o_s) != 3:
            s.comments = "You need to give atleast 3 numbers: bestX=1,bestY=2,LInfinityDistance=3."
            s.score = "0.0"
            s.save()
            return

        if int(o[2]) == int(o_s[2]):
            s.comments = "LInfinityDistance Value is correct."
            if s.updated < s.assignment.due_date:
                s.score = "20.0"
            else:
                s.score = "10.0"
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
        except ValueError:
            s.comments = "String is not a valid JSON."
        finally:
            s.save()
    else:
        s.comments = "No solution yet."
    s.save()

# Messing with Rewards
def check_hw7(s):
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

def hw6_score(len_err):
    len_correct = 100-len_err
    percent_correct = len_correct/100.0
    score = 10.0 + (100.0-10.0) * pow(percent_correct, 2.0)
    return str(score)

def check_hw6(s):
    output = s.pair.output
    try:
        if s.output_submitted:
            output = output.strip('{}()[]')
            output_submitted = s.output_submitted.strip('{}()[]')
            output = output.lower()
            output_submitted = output_submitted.lower()
            output = output.strip().split(',')
            output_submitted = output_submitted.strip().split(',')
            if len(output) == len(output_submitted):
                i = 1
                err = []
                for (o, os) in zip(output, output_submitted):
                    if not o == os:
                        err.append(i)
                    i = i + 1
                if len(err) == 0:
                    s.comments = "Solution is correct."
                    if s.updated < s.assignment.due_date:
                        s.score = "100.0"
                    else:
                        s.score = "50.0"
                else:
                    if len(err) > 100:
                        s.score = "10.0"
                    else:
                        s.score = hw6_score(len(err))
                    s.comments = str(len(err)) + " values are wrong."
                    # More detailed output
                    #if len(err) == 1:
                    #    s.comments = "Value at " + str(err[-1]) + " is wrong. You are close!"
                    #s.comments = "Values at " + " ".join(str(x)+", " for x in err[:-1]) + str(err[-1]) + " are wrong."
            else:
                s.comments = "The problem has " + str(len(output)) + " states, but your submission has " + str(len(output_submitted)) + " states."
        else:
            s.comments = "No solution yet."
    except Exception as e:
        s.comments = '%s (%s)' % (e.message, type(e))
    finally:
        s.save()

# Continuous MDP problem
def check_hw7_old(s):
    output = s.pair.output
    try:
        if s.output_submitted:
            output = output.strip('{}()[]')
            output_submitted = s.output_submitted.strip('{}()[]')
            output = output.lower()
            output = output.replace("bestactions=", "")
            output_submitted = output_submitted.lower()
            output_submitted = output_submitted.replace("bestactions=", "")
            output = output.strip().split(',')
            output_submitted = output_submitted.strip().split(',')
            if len(output) == len(output_submitted):
                i = 1
                err = []
                for (o, os) in zip(output, output_submitted):
                    if not o == os:
                        err.append(i)
                    i = i + 1
                if len(err) == 0:
                    s.comments = "Solution is correct."
                    if s.updated < s.assignment.due_date:
                        s.score = "20.0"
                    else:
                        s.score = "10.0"
                else:
                    s.score = "0"
                    s.comments = "Solution is wrong."
            else:
                s.comments = "The problem has " + str(len(output)) + " states, but your submission has " + str(len(output_submitted)) + " states."
        else:
            s.comments = "No solution yet."
    except Exception as e:
        s.comments = '%s (%s)' % (e.message, type(e))
    finally:
        s.save()

# Two Armed Bandit
def check_hw8(s):
    output = s.pair.output
    try:
        if s.output_submitted:
            output = output.strip('{}()[]')
            output_submitted = s.output_submitted.strip('{}()[]')
            output = output.lower()
            output = output.replace("value=", "")
            output_submitted = output_submitted.lower()
            output_submitted = output_submitted.replace("value=", "")
            if math.fabs(float(output) - float(output_submitted)) > 1.00:
                s.score = "0"
                s.comments = "Solution is wrong."
            else:
                s.comments = "Solution is correct."
                if s.updated < s.assignment.due_date:
                    s.score = "20.0"
                else:
                    s.score = "10.0"
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

    def get_by_student(self, s, solutions=None):
        ''' Filters IOSolution objects for student s
        :param s: Student
        :returns: List of IOSolutions generated
        '''
        if solutions:
            return solutions.filter(student=s)

        if not self.solutions:
            self.solutions = IOSolution.objects.filter(student=s)
        else:
            self.solutions = self.solutions.filter(student=s)
        return self.solutions

    def get_by_assignment(self, a, solutions=None):
        ''' Filters IOSolution objects for assignment a
        :param s: Student
        :returns: List of IOSolutions generated
        '''
        if solutions:
            return solutions.filter(assignment=a)

        if not self.solutions:
            self.solutions = IOSolution.objects.filter(assignment=a)
        else:
            self.solutions = self.solutions.filter(assignment=a)
        return self.solutions

    def update(self, pk, output=None, submit_late="false"):
        try:
            self.solutions = IOSolution.objects.filter(pk=pk)
            if len(self.solutions) == 1:
                if check_deadline(self.solutions[0].assignment) or submit_late=="true":
                    if output:
                        if len(output) > 100000:
                            return "Solution length should be less than 100,000 chars."
                        self.solutions[0].output_submitted = output
                    self.solutions[0].save()
                    return "Solution submitted."
                else:
                    return "Deadline has passed. Answer will not be recorded."
            else:
                return "Something went wrong. Only one submission allowed at a time."
        except Exception as e:
            return "%s (%s)" % (e.message, type(e))

    def update_notime(self, pk, score, comments):
        try:
            s = IOSolution.objects.get(pk=pk)
            if s:
                for field in s._meta.local_fields:
                    if field.name == "updated":
                        field.auto_now = False
                    elif field.name == "created":
                        field.auto_now_add = False

                s.score = score
                s.comments = comments
                s.save()

                for field in s._meta.local_fields:
                    if field.name == "updated":
                        field.auto_now = True
                    elif field.name == "created":
                        field.auto_now_add = True

                return "Updated"
            return "Could not find IOSolution object"
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
                check_hw4(s)
            elif a_name == "hw4":
                check_hw4(s) # Needs to change later
            elif a_name == "hw5":
                check_hw7(s)
            elif a_name == "hw6":
                check_hw6(s)
            elif a_name == "hw7":
                check_hw7(s)
            elif a_name == "hw8":
                check_hw8(s)

    def check_notime(self):
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
                check_hw7(s)
            elif a_name == "hw6":
                check_hw6(s)
            elif a_name == "hw7":
                check_hw7(s)
            elif a_name == "hw8":
                check_hw8(s)

            for field in s._meta.local_fields:
                if field.name == "updated":
                    field.auto_now = True
                elif field.name == "created":
                    field.auto_now_add = True

    def get_data(self):
        data = {}
        for sol in self.solutions:
            sd = model_to_dict(sol, fields=['output_submitted', 'score', 'comments'])
            sd['student'] = model_to_dict(sol.student, fields=['username'])
            sd['assignment'] = model_to_dict(sol.assignment, fields=['short_name'])
            sd['pair'] = model_to_dict(sol.pair, fields=['id','input', 'output'])
            sd['updated'] = sol.updated
            sd['created'] = sol.created
            data[sol.pk] = sd
        return data

    def get_stats(self):
        stats = {}
        stats['total'] = 0.0
        for s in self.solutions:
            stats['total'] += float(s.score)
        return stats
