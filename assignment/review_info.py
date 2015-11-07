from student.models import *
from assignment.models import *
import json

class review_info():
    review = None
    submission = None

    def __init__(self):
        pass

    def get_review_by_id(self, id):
        self.review = Review.objects.get(pk=id)
        return self.review
