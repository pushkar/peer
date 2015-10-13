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

class question_info():
    questions = Question.objects.none()
    def __init__(self, exam):
        self.questions = Question.objects.filter(exam=exam)

    def get_questions(self):
        return self.questions

    def set_hardness(self, q, hardness):
        q.hardness = str(hardness)
        q.save()

    def set_text(self, q, text):
        q.text = text
        q.save()

class answer_info():
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
        answers = answer_info(q)
        if answers.get_answers_count() < 2:
            return "tf"

        if np.random.choice([0, 1], 1)[0] == 0:
            return "tf"
        else:
            return "mc"

    def create_exam(self):
        details = {}
        questions = question_info(self.exam)

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
                answers = answer_info(q)
                grade = answers.get_answers_for_grading()
                for g in grade:
                    ans_dict = model_to_dict(g, fields=['label', 'text'])
                    details[q.pk]['mc']['answers'].append(ans_dict)

        self.tempexam.details = json.dumps(details)
        self.tempexam.save()
        return details
