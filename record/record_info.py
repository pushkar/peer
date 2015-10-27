from django.forms.models import model_to_dict
from student.models import *
from record.models import *
import json

class student_details_info():
    sdetails = StudentDetails.objects.none()
    def __init__(self, student):
        d = StudentDetails.objects.get_or_create(student=student)
        self.sdetails = d[0]

    def get_student_details(self):
        return self.sdetails

    def get_student_details_dict(self):
        data = model_to_dict(self.sdetails, fields=['profession', 'company', 'details'])
        if self.sdetails.objectives == None or self.sdetails.objectives == "":
            self.sdetails.objectives = json.dumps([])
            self.sdetails.save()
        objs = json.loads(self.sdetails.objectives)
        data['objectives'] = objs
        return data

    def set_profession(self, p):
        self.sdetails.profession = p
        self.sdetails.save()

    def set_company(self, c):
        self.sdetails.company = c
        self.sdetails.save()

    def add_objective(self, o):
        if self.sdetails.objectives == None or self.sdetails.objectives == "":
            objectives = []
        else:
            objectives = json.loads(self.sdetails.objectives)
        objectives.append(o)
        self.sdetails.objectives = json.dumps(objectives)
        self.sdetails.save()

    def update_details(self, d):
        self.sdetails.details = d
        self.sdetails.save()


class topics_info():
    topics = Topic.objects.none()
    def __init__(self):
        self.topics = Topic.objects.all()

    def get_all_topics(self):
        return self.topics

    def get_topics_by_group_id(self, group_id):
        self.topics = self.topics.filter(group__pk=group_id)
        return self.topics

class record_info():
    student = Student.objects.none()
    record = Record.objects.none()
    assigned = Record.objects.none()

    def __init__(self, student, assigned):
        self.student = student
        self.assigned = assigned
        r = Record.objects.get_or_create(student=student, assigned=assigned)
        self.record = r[0]

    def set_lock(self):
        self.record.locked = "1"
        self.record.save()

    def get_record(self):
        return self.record

    def get_details(self):
        if self.record.details == None or self.record.details == "":
            details = {}
            self.record.details = json.dumps(details)
            self.record.save()
        details = json.loads(self.record.details)
        data = {}
        if self.record.locked == "1":
            return data
        topics = topics_info()
        for t in topics.get_all_topics():
            t_dict = model_to_dict(t, fields=['id', 'name'])
            data[t.pk] = {}
            data[t.pk]['topic'] = t_dict
            if details.has_key(unicode(t.pk)):
                data[t.pk]['details'] = details[unicode(t.pk)]
            else:
                data[t.pk]['details'] = "Unknown"
        return data

    def add_topic_detail(self, topic_pk, topic_detail):
        if self.record.details == None or self.record.details == "":
            details = {}
            self.record.details = json.dumps(details)
            self.record.save()
        if self.record.locked == "1":
            return
        details = json.loads(self.record.details)
        details[topic_pk] = topic_detail
        self.record.details = json.dumps(details)
        self.record.save()

    def get_topic_detail(self, topic_pk):
        if self.record.details == None or self.record.details == "":
            details = {}
            self.record.details = json.dumps(details)
            self.record.save()
        details = json.loads(self.record.details)
        if details.has_key(unicode(topic_pk)):
            return details[unicode(topic_pk)]
        return "Unknown"
