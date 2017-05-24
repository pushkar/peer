import re
import math


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