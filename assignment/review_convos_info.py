from student.models import *
from assignment.models import *
from django.forms.models import model_to_dict
import json

class review_convos_info():
    convos = None

    def __init__(self):
        pass

    def get_convos(self):
        return self.convos

    def set_all_convos(self, convos):
        self.convos = convos

    def get_all_convos(self):
        self.convos = ReviewConvo.objects.all()
        return self.convos

    def get_convos_by_assignment(self, a):
        self.convos = ReviewConvo.objects.filter(review__submission__assignment=a)
        return self.convos

    def get_convos_by_review(self, r):
        self.convos = ReviewConvo.objects.filter(review=r).order_by('created')
        return self.convos

    def get_convos_by_reviews(self, r):
        self.convos = ReviewConvo.objects.filter(review__in=tuple(r))
        return self.convos

    def serialize(self, convos=None):
        if convos == None:
            convos = self.convos

        data = {}
        for c in convos:
            cd = model_to_dict(c, fields=['text'])
            data[c.pk] = cd
        return data
