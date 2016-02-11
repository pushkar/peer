from django.core import serializers
from django.forms.models import model_to_dict
from student.models import *
from exam.models import *
import numpy as np
import json

class exam_info():
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

class question_set_info():
    questions = Question.objects.none()
    def __init__(self, exam):
        self.questions = Question.objects.filter(exam=exam).order_by('pk')

    def get_questions(self):
        return self.questions

class question_info():
    question = Question.objects.none()
    def __init__(self, id):
        self.question = Question.objects.get(pk=id)

    def get_question(self):
        return self.question

    def set_hardness(self, hardness):
        self.question.hardness = str(hardness)
        self.question.save()

    def set_text(self, text):
        self.question.text = text
        self.question.save()

class answer_set_info():
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

    def set_score(self, a, student, score):
        if a.details == None or a.details == "":
            details = {}
        else:
            details = json.loads(a.details)
        details[student.username] = score
        a.details = json.dumps(details)
        a.save()

    def get_answers_for_grading(self):
        answer = []
        answer_correctness = []
        answer_inv_correctness = []
        for a in self.answers:
            answer.append(a)
            answer_correctness.append(float(a.correctness))
            answer_inv_correctness.append(1.0-float(a.correctness))

        answer_probably_correct = np.random.choice(answer, 1, answer_correctness)
        answer_probably_incorrect = np.random.choice(answer, 1, answer_inv_correctness)
        return [answer_probably_correct[0], answer_probably_incorrect[0]]

class answer_info():
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
        if self.answer.details == None or self.answer.details == "":
            details = {}
            self.answer.details = json.dumps(details)
            self.answer.save()

        details = json.loads(self.answer.details)
        self.answer.save()

    def add_grade(self, s, grade):
        if self.answer.details == None or self.answer.details == "":
            details = {}
            self.answer.details = json.dumps(details)
            self.answer.save()

        details = json.loads(self.answer.details)
        details[s.username] = str(grade)
        self.answer.details = json.dumps(details)
        self.answer.save()

def add_grade_to_answer(a, s, grade):
    if a.details == None or a.details == "":
        details = {}
        a.details = json.dumps(details)
        a.save()

    details = json.loads(a.details)
    details[s.username] = str(grade)
    a.details = json.dumps(details)
    a.save()


class tempexam_info():
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
        answers = answer_set_info(q)
        if answers.get_answers_count() < 2:
            return "tf"

        if np.random.choice([0, 1], 1)[0] == 0:
            return "tf"
        else:
            return "mc"

    def get_exam(self):
        if self.tempexam.details == None or self.tempexam.details == "":
            self.create_exam()
        return json.loads(self.tempexam.details)

    def has_finished(self):
        if self.tempexam.finished == None or self.tempexam.details == "":
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
            if self.get_question_type(q) == "tf":
                details[q.pk]['tf'] = {}
                details[q.pk]['tf']['label'] = "unknown"
                details[q.pk]['tf']['exp'] = ""
            else:
                details[q.pk]['mc'] = {}
                details[q.pk]['mc']['answers'] = []
                details[q.pk]['mc']['checked'] = []
                answers = answer_set_info(q)
                grade = answers.get_answers_for_grading()
                for g in grade:
                    ans_dict = model_to_dict(g, fields=['id', 'label', 'text'])
                    details[q.pk]['mc']['answers'].append(ans_dict)

        self.tempexam.details = json.dumps(details)
        self.tempexam.save()
        return details

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
