from student.models import *
from record.models import *
import json

class record_info():
    student = None
    record = None

    def __init__(self, student):
        self.student = student

    def get_record(self):
        try:
            self.record = Record.objects.get(student=self.student)
        except Record.DoesNotExist:
            self.add_empty_record()
        return self.record

    def add_empty_record(self):
        if Record.objects.filter(student=self.student).count() > 0:
            self.get_record()
            return False
        details = {}
        record = Record()
        record.student = self.student
        record.details = json.dumps(details)
        record.save()
        self.get_record()
        return True

    def get_details(self):
        topics = Topic.objects.all()
        if self.record.details == None or self.record.details == "":
            details = {}
            self.record.details = json.dumps(details)
            self.record.save()
        data = {}
        details = json.loads(self.record.details)

        for t in topics:
            if not details.has_key(unicode(t.pk)):
                data[t.name] = ""
            else:
                data[t.name] = details[unicode(t.pk)]
        return data

    def add_details(self, topic_pk, topic_detail):
        self.get_record()
        details = json.loads(self.record.details)
        details[topic_pk] = topic_detail
        self.record.details = json.dumps(details)
        self.record.save()

    def get_topic_details(self, topic_pk):
        details = self.get_details()
        if details.has_key(topic_pk):
            return details[topic_pk]
        return ""


class topic_info():
    def __init__(self):
        pass

    def get_all_topics():
        topics = Topic.objects.all()
        return topics

    def add_topic(name, details="", order=0):
        topic = Topic()
        topic.name = name
        topic.details = details
        topic.order = order
        topic.save()

    def remove_topic(name):
        topic = Topic.object.get(name=name)
        topic.delete()
