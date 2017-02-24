from django.core import serializers
from django.forms.models import model_to_dict
from student.models import *
from exam.models import *

import numpy as np
import requests
import json
import random
import logging

def setup_logger(logger_name, log_file=None, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("[EXAM] %(message)s")
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(streamHandler)

setup_logger("exam")
log = logging.getLogger("exam")

# Helper Functions
def get_or_set_json(_str):
    '''
    Sets or gets a json based database input.
    Sets it to an empty map.
    '''
    if _str is None or _str == "":
        details = {}
    else:
        try:
            details = json.loads(_str)
        except:
            details = {}
    return details

# Classes to work with Model objects
############################### EXAM ###############################
class exam_info(object):
    '''
    Works with the Model Exam
    '''
    exam = Exam.objects.none()
    def __init__(self, short_name):
        exam = Exam.objects.get_or_create(short_name=short_name)
        self.exam = exam[0]

    def set_name(self, name):
        self.exam.name = name
        self.exam.save()

    def set_start_end_time(self, start, end):
        self.exam.start_time = start
        self.exam.end_time = end
        self.exam.save()

    def get_exam(self):
        return self.exam

############################ STUDENT_INFO ############################
class studentinfo_info(object):
    '''
    Works with the StudentInfo
    '''
    info = StudentInfo.objects.none()
    def __init__(self, student):
        info = StudentInfo.objects.get_or_create(student=student)
        if info[1] is True:
            log.info("StudentInfo object was created for %s" % (student))
        self.info = info[0]

    def set_proficiency(self, proficiency):
        self.info.proficiency = proficiency
        self.info.save()

    def get_proficiency(self):
        return self.info.proficiency

############################## STRATEGY ###############################
class strategy_info(object):
    strategy = Strategy.objects.none()
    def __init__(self, name):
        try:
            self.strategy = Strategy.objects.get(name=name)
        except Exception as e:
            log.error(e.message)

    def get_params(self):
        return self.strategy.params

############################ QUESTION_INFO #############################
class question_info(object):
    '''
    Works with one question
    '''
    question = Question.objects.none()
    def __init__(self, id):
        self.question = Question.objects.get(pk=id)

    def get_question(self):
        return self.question

    def set_hardness(self, strategy, hardness):
        strategy = strategy.name
        hardness_details = get_or_set_json(self.question.hardness)
        hardness_details[strategy] = hardness
        self.question.hardness = json.dumps(hardness_details)
        self.question.save()

    def get_hardness(self, strategy):
        strategy = strategy.name
        hardness_details = get_or_set_json(self.question.hardness)
        if strategy not in hardness_details:
            hardness_details[strategy] = "0.0"
            self.question.hardness = json.dumps(hardness_details)
            self.question.save()

        return float(hardness_details[strategy])

    def set_text(self, text):
        self.question.text = text
        self.question.save()


### For many questions
class question_set_info(object):
    '''
    Works with a set of questions.
    '''
    questions = Question.objects.none()
    def __init__(self, exam):
        self.questions = Question.objects.filter(exam=exam).order_by('pk')

    def get_questions(self):
        return self.questions

############################## GRADING ###############################
class grading_info(object):
    '''
    Works with the Grading class
    '''
    grade = Grading.object.none()
    def __init__(self, student, mc):
        grade = Grading.objects.get_or_create(stduent=student, mc=mc)
        if grade[1] is True:
            log.info("Grading object was created by %s" % (student))
        self.grade = grade[0]

    def get_grade(self):
        return self.grade.grade

    def set_grade(self, grade):
        self.grade.grade = grade
        self.grade.save()
