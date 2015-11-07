from student.models import *
from assignment.models import *
import json

class review_convos_info():
    convos = None

    def __init__(self):
        pass

    def set_all_convos(self, convos):
        self.convos = convos

    def get_all_convos(self):
        self.convos = ReviewConvo.objects.all()
        return self.convos
