from student.models import *
from record.models import *
import json

class record_info():
    student = None
    record = None

    def __init__(self, student):
        self.student = student

    def get_record(self):
        self.record = Record.objects.get(student=self.student)
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
        return True

    def get_details(self):
        if self.record.details == None or self.record.details == "":
            details = {}
            self.record.details = json.dumps(details)
            self.record.save()
        return json.loads(self.record.details)

    def add_details(self, topic_name, topic_detail):
        details = get_details()
        details['topic_name'] = topic_detail
        self.record.details = json.dumps(details)
        self.record.save()

    def get_topic_details(self, topic_name):
        details = get_details()
        if details.has_key(topic_name):
            return details[topic_name]
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
