from student.models import *
from assignment.models import *
import json

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

class review_convo_info():
    review = None

    def __init__(self):
        pass

    def set_convo(self, convo):
        self.review = convo

    def get_convo_by_id(self, id):
        self.review = ReviewConvo.objects.get(pk=id)

    def get_by_submission_and_assigned(self, submission, student):
        self.review = ReviewConvo.objects.get(submission=submission, assigned=student)

    def check_details(self):
        if self.review.details == None or self.review.details == "":
            details = {}
            details['likes'] = list()
            self.review.details = json.dumps(details)
            self.review.save()
            return True
        return False

    def add_like(self, s):
        self.check_details()
        details = json.loads(self.review.details)
        if s.username not in details['likes']:
            details['likes'].append(s.username)
        self.review.details = json.dumps(details)
        self.review.save()

    def remove_like(self, s):
        self.check_details()
        details = json.loads(self.review.details)
        details['likes'].remove(s.username)
        self.review.details = json.dumps(details)
        self.review.save()

    def get_total_likes(self):
        self.check_details()
        details = json.loads(self.review.details)
        return len(details['likes'])

    def has_liked(self, s):
        self.check_details()
        details = json.loads(self.review.details)
        if s.username in details['likes']:
            return "True"
        return "False"

    def get_likes_info(self, s):
        self.check_details()
        details = json.loads(self.review.details)
        info = {}
        info['total_likes'] = len(details['likes'])
        if s.username in details['likes']:
            info['has_liked'] = True
        else:
            info['has_liked'] = False
        return info

    def change_score(self, score):
        self.review.score = score
        self.review.save()

    def get_score(self):
        return self.review.score
