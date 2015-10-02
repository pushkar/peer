from student.models import *
from assignment.models import *
import json

class submission_info():
    submissions = None
    message = ""

    def __init__(self):
        pass

    def get_all_submissions(self):
        self.submissions = Submission.objects.all()
        return self.submissions

    def filter_by_student(self, s):
        self.submissions = self.submissions.filter(student=s)
        return self.submissions

    def filter_by_assignment(self, a):
        self.submissions = self.submissions.filter(assignment=a)
        return self.submissions

    def get_by_student_and_assignment(self, s, a):
        self.submissions = Submission.objects.get(student=s, assignment=a)
        return self.submissions

    def get_by_id(self, id):
        self.submission = Submission.objects.get(pk=id)
        return self.submission

    def get_message(self):
        return self.message

    def add_file(self, submission, f_name, f_link):
        files = json.loads(submission.files)
        files[f_link] = f_name
        submission.files = json.dumps(files)
        submission.save()

    def get_files(self, submission):
        return json.loads(submission.files)

    def assign_reviewers(self, submission=None):
        if submission == None:
            return False

        #optin_reviewers = OptIn.objects.filter(value=True, student__usertype='student').select_related('student')
        optin_reviewers = OptIn.objects.filter(value=True).select_related('student')

        ## All reviewers who have opted in
        reviewers_all = set()
        for optins in optin_reviewers:
            reviewers_all.add(optins.student)

        a = submission.assignment
        ## Check if they have opted in
        if submission.student not in reviewers_all:
            reviewers_all.discard(submission.student)
            self.message += str(submission.student.username) + " not opted in the peer review program yet"
            return False

        ## Skip if 3 reviewers have been assigned
        if Review.objects.filter(submission=submission).count() >= 3:
            self.message += str(submission.student.username) + " has already been assigned."
            return False

        ## Remove the current submission student from reviewers set
        ## If cannot remove, then they probably did not opt in
        if submission.student in reviewers_all:
            reviewers_all.discard(submission.student)

        ## Remove reviewers who haven't submitted an assignment
        reviewers_nosub = set()
        for r in reviewers_all:
            if Submission.objects.filter(student=r, assignment=a).count() <= 0:
                reviewers_nosub.add(r)
        reviewers_all -= reviewers_nosub

        ## Remove all reviewers who have been assigned 3 reviews
        reviewers_assigned = set()
        for r in reviewers_all:
            if Review.objects.filter(assigned=r, submission__assignment=a).count() >= 3:
                reviewers_assigned.add(r)

        reviewers_all -= reviewers_assigned

        ## Find 3 random reviewers
        reviewer_count = 0
        reviewers_3 = set()
        if len(reviewers_all) == 0:
            self.message = "Not enough reviewers to match you. Try again later."
            return False
        elif len(reviewers_all) < 3:
            reviewers_3 = random.sample(reviewers_al, len(reviewers))
            self.message = "Not enough reviewers to match you. Try again later to find more reviewers."
            return False
        else:
            reviewers_3 = random.sample(reviewers_all, 3)

        for r in reviewers_3:
            if Review.objects.get_or_create(submission=submission, assigned=r, score="0", details="")[1]:
                reviewer_count += 1

        self.message = "Assigned " + str(reviewer_count) + " reviewers"
        return True
