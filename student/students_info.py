from student.models import *
import json

class students_info():
    students = None
    message = ""

    def __init__(self):
        pass

    def get_all_students(self):
        self.students = Student.objects.all()
        return self.students

    def get_all_tas(self):
        self.students = Student.objects.filter(usertype="ta")
        return self.students
