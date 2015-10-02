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

class review_convo_info():
    review = None

    def __init__(self):
        pass

    def get_review_by_pk(self, pk):
        self.review = ReviewConvo.objects.get(pk=pk)

    def get_by_submission_and_assigned(self, submission, student):
        self.review = ReviewConvo.objects.get(submission=submission, assigned=student)

    def add_like(self, s):
        details = self.review.details
        if not details.has_key('likes'):
            details['likes'] = []
        details['likes'].append(s)
        self.review.details = details
        self.review.save()

    def remove_like(self, s):
        self.review.details['likes'].remove(s)
        self.review.save()

    def get_total_likes(self):
        return self.review.details['likes'].count()

    def has_liked(self, s):
        if s in self.review.details['likes']:
            return True
        return False

    def change_score(self, score):
        self.review.score = score
        self.review.save()

    def get_score(self):
        return self.review.score
