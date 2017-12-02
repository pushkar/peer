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
    iopairs_count = len(iopairs.get(a))
    if n > iopairs_count:
        n = iopairs_count

    iosolutions_count = IOSolution.objects.filter(student=s, assignment=a).count()
    if iosolutions_count > n:
        solutions = IOSolution.objects.filter(student=s, assignment=a)
        log.info("There are extra %s IOSolutions" % (iosolutions_count-n))
        _n = 0
        for sol in solutions:
            _n = _n + 1
            if _n > n:
                log.info("Deleting %s" % sol)
                sol.delete()

    elif iosolutions_count < n:
        _n = n - iosolutions_count
        log.info("%s Generating %s IOPairs" % (s, _n))
        pairs = iopairs.get_random(a, _n)
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
        :param a: Assignment
        :returns: List of IOSolutions generated
    '''
    if solutions:
        return solutions.filter(assignment=a)

    return IOSolution.objects.filter(assignment=a)

def get_by_assignment_scores(a):
    ''' Filters IOSolution objects for assignment a
        :param a: Assignment
        :returns: List of IOSolutions generated with student ids
        Specifically written for download_as_csv
    '''
    scores = {}
    solutions = IOSolution.objects.select_related().filter(assignment=a)
    for sol in solutions:
        if sol.student not in scores:
            scores[sol.student] = 0.0
        scores[sol.student] += sol.score
    return scores

def sol_to_dict(sol):
    d = {
        'id': sol.id,
        'student': {
            'username': sol.student.username,
            'firstname': sol.student.firstname,
            'lastname': sol.student.lastname,
            'email_tsq': sol.student.email_tsq
        },
        'solution': {
            'submission': sol.output_submitted,
            'score': sol.score,
            'comments': sol.comments,
            'count': sol.count,
            'created': str(sol.created),
            'updated': str(sol.updated)
        },
        'pair': {
            'input': sol.pair.input,
            'output': sol.pair.output
        }
    }
    return d

def get_by_assignment_all(a):
    """ Filters IOSolution objects for assignment a
        :param a: Assignment
        :returns: List of IOSolutions generated
    """
    scores = []
    count = 0
    solutions = IOSolution.objects.select_related().filter(assignment=a)
    for sol in solutions:
        d = sol_to_dict(sol)
        scores.append(d)
    return scores


def get_none():
    return IOSolution.objects.none()

def get_by(s, a):
    return IOSolution.objects.filter(student=s, assignment=a)

def get_by_id(pk):
    solution = IOSolution.objects.filter(pk=pk)
    if len(solution) > 1:
        log.error("Found more than 1 solution")
    return solution

def get_by_id_all(pk):
    sol = IOSolution.objects.filter(pk=pk)
    return sol_to_dict(sol[0])

def update(solution, output=None, submit_late="false"):
    try:
        solution = solution[0]
        if solution.count >= 10:
            return "Max submissions excedded."
        if check_deadline(solution.assignment) or submit_late == "true":
            if output:
                if len(output) > 100000:
                    return "Solution length should be less than 100,000 chars."
                solution.output_submitted = output
            solution.count = solution.count + 1
            solution.save()
            return "Solution submitted. You have %s submissions available." % (10 - solution.count)
        else:
            return "Deadline has passed. Answer will not be recorded."
    except Exception as e:
        return "Exception: %s" % (e)

def check(solutions):
    for s in solutions:
        a_name = s.assignment.short_name
        if a_name == "bandit":
            hw_check.check_two_armed_bandit(s)
        if a_name == "k_arm":
            hw_check.check_k_armed_bandit(s)
        elif a_name == "mdp":
            hw_check.check_valid_json(s)
        elif a_name == "bar":
            hw_check.check_bar_brawl(s)
        else:
            hw_check.check_floating_point_answer(s)

def get_stats(solutions):
    stats = {}
    stats['total'] = 0.0
    for s in solutions:
        stats['total'] += float(s.score)
    return stats
