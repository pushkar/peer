from student.models import *
from assignment.models import *
from review_convo_info import *
from review_convos_info import *
from django.forms.models import model_to_dict
import numpy as np
import json

class reviews_info():
    reviews = None
    submissions = None

    def __init__(self):
        pass

    def get_reviews(self):
        return self.reviews

    def get_all_reviews(self):
        self.reviews = Review.objects.all()
        return self.reviews

    def get_reviews_by_assignment(self, assignment, order_by='pk'):
        self.reviews = Review.objects.filter(submission__assignment=assignment).order_by(order_by, 'pk')
        return self.reviews

    def get_reviews_by_assignment_and_usertype(self, assignment, usertype, order_by='pk'):
        self.reviews = Review.objects.filter(submission__assignment=assignment, assigned__usertype=usertype).order_by(order_by, 'pk')
        return self.reviews

    def get_reviews_by_submission(self, sub):
        self.reviews = Reviews.objects.filter(submission=sub)
        return self.reviews

    def filter_by_submission(self, sub, reviews=None):
        if reviews == None:
            reviews = self.reviews
        reviews = reviews.filter(submission=sub)
        return reviews

    def filter_by_student(self, s, reviews=None):
        if reviews == None:
            reviews = self.reviews
        reviews = reviews.filter(submission__student=s)
        return reviews

    def filter_by_assigned(self, s, reviews=None):
        if reviews == None:
            reviews = self.reviews
        reviews = reviews.filter(assigned=s)
        return reviews

    def serialize(self, reviews=None):
        if reviews == None:
            reviews = self.reviews
        data = {}
        for r in reviews:
            rd = model_to_dict(r, fields=['score'])
            rd['assigned_username'] = r.assigned.username
            rd['assigned_usertype'] = r.assigned.usertype
            data[r.pk] = rd
        return data

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

    def get_stats(self, reviews=None):
        if reviews == None:
            reviews = self.reviews

        scores = []
        len_scores = 0
        for r in reviews:
            if r.score:
                len_scores += 1
                score = float(r.score)
                if score > 0:
                    scores.append(score)


        if len(reviews) == 0:
            # Add a random value to avoid div by zero error
            scores.append(0)
            len_reviews = 1
        else:
            len_reviews = len(reviews)

        if len(scores) == 0:
            scores.append(0)

        stats = {}
        stats['mean'] = round(np.mean(scores), 2)
        stats['std'] = round(np.std(scores), 2)
        stats['median'] = np.median(scores)
        stats['completed'] = float(len_scores)/float(len_reviews)*100.0
        stats['completed'] = round(stats['completed'], 2)
        stats['scores'] = scores
        stats['total_assigned'] = len_reviews
        return stats


    def gather_review_convo_info(self, reviews=None):
        if reviews == None:
            reviews = self.reviews

        review_convos = review_convos_info()
        return review_convos.get_convos_by_reviews(reviews)
