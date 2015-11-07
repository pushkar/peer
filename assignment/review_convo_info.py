from student.models import *
from assignment.models import *
import json

class review_convo_info():
    convo = None

    def __init__(self):
        pass

    def set_convo(self, convo):
        self.convo = convo

    def get_convo_by_id(self, id):
        self.convo = ReviewConvo.objects.get(pk=id)

    def get_by_submission_and_assigned(self, submission, student):
        self.convo = ReviewConvo.objects.get(submission=submission, assigned=student)

    def check_details(self):
        if self.convo.details == None or self.convo.details == "":
            details = {}
            details['likes'] = list()
            self.convo.details = json.dumps(details)
            self.convo.save()
            return True
        return False

    def add_like(self, s):
        self.check_details()
        details = json.loads(self.convo.details)
        if s.username not in details['likes']:
            details['likes'].append(s.username)
        self.convo.details = json.dumps(details)
        self.convo.save()

    def remove_like(self, s):
        self.check_details()
        details = json.loads(self.convo.details)
        details['likes'].remove(s.username)
        self.convo.details = json.dumps(details)
        self.convo.save()

    def get_total_likes(self):
        self.check_details()
        details = json.loads(self.convo.details)
        return len(details['likes'])

    def has_liked(self, s):
        self.check_details()
        details = json.loads(self.convo.details)
        if s.username in details['likes']:
            return "True"
        return "False"

    def get_likes_info(self, s):
        self.check_details()
        details = json.loads(self.convo.details)
        info = {}
        info['total_likes'] = len(details['likes'])
        if s.username in details['likes']:
            info['has_liked'] = True
        else:
            info['has_liked'] = False
        return info
