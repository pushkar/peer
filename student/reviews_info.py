from student.models import *
from assignment.models import *

class reviews_info():
    reviews = None
    submissions = None

    def __init__(self):
        pass

    def get_all_reviews(self):
        self.reviews = Review.objects.all()

    def get_reviews_by_submission(self, sub):
        self.reviews = Reviews.objects.filter(submission=sub)

    def filter_by_student(self, s):
        reviews = self.reviews.filter(submission__student=s)
        return reviews

    def filter_by_assigned(self, s):
        reviews = self.reviews.filter(assigned=s)
        return reviews

    def get_data(self, reviews=None):
        if reviews == None:
            reviews = self.reviews
        data = {}
        for r in reviews:
            if not data.has_key(r.submission.student):
                data[r.submission.student] = {}

            if not data[r.submission.student].has_key(r.submission.assignment):
                data[r.submission.student][r.submission.assignment] = []

            data[r.submission.student][r.submission.assignment].append(r)

        return data
