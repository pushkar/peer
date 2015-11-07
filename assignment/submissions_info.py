from student.models import *
from assignment.models import *
import json

class submissions_info():
    submissions = None
    message = ""

    def __init__(self):
        pass

    def get_all_submissions(self):
        self.submissions = Submission.objects.all()
        return self.submissions

    def filter_by_student(self, s, submissions=None):
        if submissions == None:
            submissions = self.submissions
        submissions = submissions.filter(student=s)
        return submissions

    def filter_by_assigned(self, s, submissions=None):
        if submissions == None:
            submissions = self.submissions
        submissions = submissions.filter(assigned=s)
        return submissions

    def filter_by_assignment(self, a, submissions=None):
        if submissions == None:
            submissions = self.submissions
        submissions = submissions.filter(assignment=a)
        return submissions
        
