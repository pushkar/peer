from student.models import *
from assignment.models import *
import json

class submission_info():
    submission = None
    message = ""

    def get_by_student_and_assignment(self, s, a):
        try:
            self.submission = Submission.objects.get(student=s, assignment=a)
        except Submission.DoesNotExist:
            self.submission = None
        return self.submission

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
            submission = self.submission

        optin_reviewers = OptIn.objects.filter(value=True, student__usertype='student').select_related('student')
        ## All reviewers who have opted in
        reviewers_all = set()
        for optins in optin_reviewers:
            reviewers_all.add(optins.student)

        a = submission.assignment
        ## Check if they have opted in
        if submission.student not in reviewers_all:
            reviewers_all.discard(submission.student)
            self.message += "You have not opted in the peer review program yet."
            return False

        ## Skip if 3 reviewers have been assigned
        if Review.objects.filter(submission=submission).count() >= 3:
            self.message += "You have already been assigned 3 reviewers."
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
        if len(reviewers_all) < 3:
            self.message = "Not enough reviewers to match you. Try again later to find more reviewers."
            return False
        else:
            reviewers_3 = random.sample(reviewers_all, 3)

        for r in reviewers_3:
            if Review.objects.get_or_create(submission=submission, assigned=r, score="0", details="")[1]:
                reviewer_count += 1

        self.message = "Assigned " + str(reviewer_count) + " reviewers."
        return True

    def assign_submissions(self, assignment, student=None):
        if student == None:
            return False

        if Review.objects.filter(submission__assignment=assignment, assigned=student).count() >= 3:
            self.message += "You have already been assigned 3 submissions to review."
            return False

        optin_reviewers = OptIn.objects.filter(value=True, student__usertype='student').select_related('student')
        optins = set()
        for opt in optin_reviewers:
            optins.add(opt.student)

        if student not in optins:
            self.message += "You not opted in the peer review program yet."
            return False

        ## All submissions
        student_has_submitted = False
        submissions_all = set()
        submissions = Submission.objects.filter(assignment=assignment)
        for s in submissions:
            submissions_all.add(s)
            if s.student == student:
                student_has_submitted = True

        if not student_has_submitted:
            self.message += "You need to submit an assignment to review others."
            return False

        submissions_discard = set()
        for s in submissions_all:
            # Remove the student's submission
            if s.student == student:
                submissions_discard.add(s)

            # Remove if 3 reviews are assigned
            if Review.objects.filter(submission=s).count() >= 3:
                submissions_discard.add(s)

            if s.student not in optins:
                submissions_discard.add(s)
        submissions_all -= submissions_discard

        reviews_assigned = 0
        if len(submissions_all) < 3:
            # I am not sure if I should still assign these submissions
            submissions_3 = random.sample(submissions_all, len(submissions_all))
            self.message += "Not enough submissions to review."
            return False
        else:
            submissions_3 = random.sample(submissions_all, 3)
            for s in submissions_3:
                if Review.objects.get_or_create(submission=s, assigned=student, score="0", details="")[1]:
                    reviews_assigned += 1

        self.message = "Assigned " + str(reviews_assigned) + " reviews."
        return True
