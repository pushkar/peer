from student.models import Student

class students_info(object):
    def __init__(self):
        self.students = None

    def get_all_students(self):
        self.students = Student.objects.all()
        return self.students

    def get_all_tas(self):
        self.students = Student.objects.filter(usertype="ta")
        return self.students
