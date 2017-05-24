from django.core import serializers
from django.forms.models import model_to_dict
from student.models import *
from exam.models import *
from exam.exam_utils import *

import numpy as np
import requests
import json
import random


class answer_set_info(object):
    '''
    Works with a set of answers
    '''
    answers = Answer.objects.none()
    def __init__(self, question):
        self.answers = Answer.objects.filter(question=question)

    def get_answers(self):
        return self.answers

    def get_answers_count(self):
        return len(self.answers)

    def set_label_text(self, a, label, text):
        a.label = label
        a.text = text
        a.save()

    def get_answers_sample_random(self, n):
        if len(self.answers) < n:
            return self.answers
        return random.sample(self.answers, 2)

    def get_answers_sample_correctness(self, n, inverted_correctness=False):
        """
        TODO Deprecated?
        """
        answer = []
        for a in self.answers:
            answer.append(a)
            if inverted_correctness:
                answer_correctness.append(1.0 - float(a.correctness))
            else:
                answer_correctness.append(float(a.correctness))

        return np.random.choice(answer, n, answer_correctness)

class answer_info(object):
    '''
    Works with an answer
    '''
    answer = Answer.objects.none()
    def __init__(self):
        pass

    def get_answer(self):
        return self.answer

    def get_answer_by_student_and_question(self, s, q):
        # what if a returns more than one answers?
        a = Answer.objects.get_or_create(student=s, question=q)
        self.answer = a[0]
        return a[1]

    def get_answer_by_id(self, id):
        self.answer = Answer.objects.get(pk=id)

    def set_label_and_text(self, l, t):
        self.answer.label = l
        self.answer.text = t
        self.answer.save()

    def calculate_correctness(self):
        '''
        TODO
        '''
        details = get_or_set_json(self.answer.details)
        self.answer.details = json.dumps(details)
        self.answer.save()

    def add_grade(self, s, grade):
        details = get_or_set_json(self.answer.details)
        details[s.username] = str(grade)
        self.answer.details = json.dumps(details)
        self.answer.save()

############################## TEMPEXAM ###############################
class tempexam_info(object):
    '''
    Works with TempExam model.
    Students are answering into TempExam. They save the exam here.
    '''
    exam = Exam.objects.none()
    tempexam = TempExam.objects.none()
    def __init__(self, s, e):
        try:
            self.exam = e
            tempexam = TempExam.objects.get_or_create(exam=e, student=s)
            self.tempexam = tempexam[0]
        except TempExam.DoesNotExist:
            pass

    def get_question_type(self, q):
        question_type = "tf"
        args = []

        answers = answer_set_info(q)
        if answers.get_answers_count() < 2:
            return question_type, args

        if q.strategy == "tf":
            pass

        if q.strategy == "random":
            if random.uniform(0, 1) > 0.5:
                question_type = "mc"
                args = random.sample(answers.get_answers(), 2)

        return question_type, args

    def get_exam(self):
        if self.tempexam.details is None or self.tempexam.details == "":
            self.create_exam()
        return json.loads(self.tempexam.details)

    def has_finished(self):
        if self.tempexam.finished is None or self.tempexam.details == "":
            self.tempexam.finished = "0"
            self.tempexam.save()
        finished = self.tempexam.finished
        if finished == "1":
            return True
        return False

    def create_exam(self):
        details = {}
        questions = question_set_info(self.exam)

        for q in questions.get_questions():
            details[q.pk] = {}
            details[q.pk]['question'] = model_to_dict(q, fields=['id', 'text'])
            type, answers = self.get_question_type(q)
            if type == "tf":
                details[q.pk]['tf'] = {}
                details[q.pk]['tf']['label'] = "unknown"
                details[q.pk]['tf']['exp'] = ""
            elif type == "mc":
                details[q.pk]['mc'] = {}
                details[q.pk]['mc']['answers'] = []
                details[q.pk]['mc']['checked'] = []
                for a in answers:
                    ans_dict = model_to_dict(a, fields=['id', 'label', 'text'])
                    details[q.pk]['mc']['answers'].append(ans_dict)

        self.tempexam.details = json.dumps(details)
        self.tempexam.save()
        return details

    def check_exam(self, request_data):
        '''
        Check explanations of the exam and find if they make sense or not.
        '''
        ret_bool = True
        ret = {}
        details = json.loads(self.tempexam.details)

        for qid, qans in details.iteritems():
            if qans.has_key('tf'):
                q_label = "q" + str(qid) + "_label"
                q_exp = "q" + str(qid) + "_exp"
                if request_data.has_key(q_exp):
                    if len(request_data[q_exp]) > 0:
                        exp_ = request_data[q_exp][0]
                        id_ = qid
                        if len(exp_) == 0:
                            ret_bool = False
                            exp_ = "No explanation was provided."
                            ret[id_] = exp_
                        else:
                            url = 'http://thegraduationmachine.cc.gt.atl.ga.us:8081/v2/check'
                            data = 'language=en-US&text=' + exp_
                            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
                            r = requests.post(url, data=data, headers=headers)
                            ret[id_] = ""
                            if r.status_code == 200:
                                lang_analysis = json.loads(r.text)
                                errors_len = len(lang_analysis["matches"])
                                if errors_len > 0:
                                    ret_bool = False
                                    for errors in lang_analysis["matches"]:
                                        ret[id_] += errors["message"]

        return ret_bool, ret

    def save_exam(self, request_data):
        details = json.loads(self.tempexam.details)

        for qid, qans in details.iteritems():
            if qans.has_key('tf'):
                q_label = "q" + str(qid) + "_label"
                q_exp = "q" + str(qid) + "_exp"
                if request_data.has_key(q_label):
                    if len(request_data[q_label]) > 0:
                        details[qid]['tf']['label'] = request_data[q_label][0]
                if request_data.has_key(q_exp):
                    if len(request_data[q_exp]) > 0:
                        details[qid]['tf']['exp'] = request_data[q_exp][0]

            if qans.has_key('mc'):
                q_mc = "q" + str(qid) + "_mc"
                if request_data.has_key(q_mc):
                    details[qid]['mc']['checked'] = []
                    for aid in request_data[q_mc]:
                        details[qid]['mc']['checked'].append(aid)

        self.tempexam.details = json.dumps(details)
        self.tempexam.save()
        return True

    def submit_exam(self):
        s = self.tempexam.student
        details = json.loads(self.tempexam.details)

        for qid, qans in details.iteritems():
            q = question_info(qid).get_question()
            if qans.has_key('tf'):
                tf_qans = details[qid]['tf']
                if tf_qans.has_key('label') and tf_qans.has_key('exp'):
                    if tf_qans['label'] == "True" or tf_qans['label'] == "False" and len(tf_qans['exp']) > 0: # check other conditions too.
                        a = answer_info()
                        a.get_answer_by_student_and_question(s, q)
                        a.set_label_and_text(tf_qans['label'], tf_qans['exp'])

            if qans.has_key('mc'):
                mc_qans = details[qid]['mc']
                if mc_qans.has_key('answers') and mc_qans.has_key('checked'):
                    mc_qans_all = []
                    for mc in mc_qans['answers']:
                        mc_qans_all.append(mc['id'])
                    mc_qans_correct = []
                    # convert unicode ids to ints
                    for mc_ in mc_qans['checked']:
                        mc_qans_correct.append(int(mc_))
                    mc_qans_incorrect = [x for x in mc_qans_all if x not in mc_qans_correct]
                    for aid in mc_qans_correct:
                        a = answer_info()
                        a.get_answer_by_id(aid)
                        a.add_grade(s, 1)
                    for aid in mc_qans_incorrect:
                        a = answer_info()
                        a.get_answer_by_id(aid)
                        a.add_grade(s, 0)

        if not self.has_finished():
            self.tempexam.finished = "1"
            self.tempexam.save()
        return True

    def delete_exam(self):
        if not self.has_finished():
            self.tempexam.finished = "1"
            self.tempexam.save()
        # Never delete the tempexam
        # self.tempexam.delete()
