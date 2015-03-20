from django.db import models
from django import forms
from django.contrib import admin, messages
from django.forms.widgets import RadioSelect
from student.models import *

import csv
import random
import urllib2

class Assignment(models.Model):
    short_name = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return unicode(self.name)

class AssignmentPage(models.Model):
    assignment = models.ForeignKey(Assignment)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(max_length=15000)

class Submission(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)

    def __unicode__(self):
        return unicode("Submission of " + unicode(self.student))

class SubmissionFile(models.Model):
    submission = models.ForeignKey(Submission)
    link = models.CharField(max_length=1000)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.submission)

# Each Review is assigned to someone and has a score
class Review(models.Model):
    submission = models.ForeignKey(Submission)
    assigned = models.ForeignKey(Student)
    score = models.CharField(max_length=10)
    details = models.CharField(default=None, max_length=1000)

    def __unicode__(self):
        return unicode("Review for " + unicode(self.submission.student) + " - " + unicode(self.pk))

# Who can access the review other than the one who it was assigned to?
class Permission(models.Model):
    review = models.ForeignKey(Review)
    student = models.ManyToManyField(Student)

class ReviewConvo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review)
    student = models.ForeignKey(Student)
    text =  models.CharField(max_length=10000, null=True)
    score = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ['created']
        get_latest_by = ['created']


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date')
    actions = ['populate_submissions']

    def populate_submissions(self, request, queryset):
        files_count = 0
        files_total = 0
        submissions_count = 0

        for assignment in queryset:
            try:
                g = Global.objects.get(key="submissions")
                self.message_user(request, "Reading from %s." % g.value)
                submission_str = urllib2.urlopen(g.value).read()
                reader = csv.reader(submission_str.split('\n'), delimiter=',')
                for row in reader:
                    files_total = files_total + 1
                    student = Student.objects.get(username=row[0])
                    if student:
                        submission = Submission.objects.get_or_create(student=student, assignment=assignment)
                        if submission[1]:
                            submissions_count += 1
                        if SubmissionFile.objects.get_or_create(submission=submission[0], name=row[1], link=row[2])[1]:
                            files_count += 1
            except:
                self.message_user(request, "Could not find submission file.")


        self.message_user(request, "%s student submissions were added. %s of %s files were added." % (str(submissions_count), str(files_count), str(files_total)) )

    populate_submissions.short_description = "Populate with Submissions"

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

class SubmissionFileAdmin(admin.ModelAdmin):
    list_display = ('submission', 'name', 'link')
    search_fields = ('submission__student__lastname', 'submission__student__firstname', 'submission__student__username')


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'student', 'assignment')
    search_fields = ('student__lastname', 'student__firstname', 'student__username', 'student__group_id')
    actions = ['assign_reviewers',  'assign_ta_review']
    list_filter = ('assignment__name',)


    def assign_reviewers(self, request, queryset):
        submission_count = len(queryset)
        reviewer_count = 0

        optin_reviewers = OptIn.objects.filter(value=True, student__usertype='student').select_related('student')

        ## All reviewers who have opted in
        reviewers_all = set()
        for optins in optin_reviewers:
            reviewers_all.add(optins.student)

        for submission in queryset:
            ## Check if they have opted in
            if submission.student not in reviewers_all:
                self.message_user(request, "%s has not opted in." % str(submission.student), level=messages.WARNING)
                continue

            ## Skip if 3 reviewers have been assigned
            if Review.objects.filter(submission=submission).count() >= 3:
                self.message_user(request, "%s has already been assigned." % str(submission), level=messages.WARNING)
                continue

            ## All reviewers who have opted in and are a part of this group
            reviewers = set()
            for r in reviewers_all:
                if submission.student.group_id == r.group_id:
                    reviewers.add(r)

            ## Remove the current submission student from reviewers set
            ## If cannot remove, then they probably did not opt in
            if submission.student in reviewers:
                reviewers.remove(submission.student)

            ## Remove all reviewers who have been assigned 3 reviews
            reviewers_assigned = set()
            for r in reviewers:
                if Review.objects.filter(assigned=r).count() >= 3:
                    reviewers_assigned.add(r)

            reviewers -= reviewers_assigned
            reviewers_all -= reviewers_assigned # Also remove from the _all set

            ## Find 3 random reviewers
            reviewers_3 = set()
            if len(reviewers) == 0:
                self.message_user(request, "Not enough reviewers to match %s in this group." % str(submission.student), level=messages.WARNING)
            elif len(reviewers) < 3:
                reviewers_3 = random.sample(reviewers, len(reviewers))
            else:
                reviewers_3 = random.sample(reviewers, 3)

            for r in reviewers_3:
                if Review.objects.get_or_create(submission=submission, assigned=r, score="0", details="")[1]:
                    reviewer_count += 1


        self.message_user(request, "Assigned %s reviewers to %s submissions." % (str(reviewer_count), str(submission_count)) )

    assign_reviewers.short_description = "Assign 3 Reviewers"

    def assign_ta_review(self, request, queryset):
        submission_count = len(queryset)
        reviewer_count = 0

        for submission in queryset:
            tas = Student.objects.filter(group_id=submission.student.group_id, usertype="ta")
            for ta in tas:
                if Review.objects.get_or_create(submission=submission, assigned=ta, score="0", details="")[1]:
                    reviewer_count += 1

        self.message_user(request, "Assigned %s reviewers to %s submissions." % (str(reviewer_count), str(submission_count)) )


    assign_ta_review.short_description = "Assign TA to review submissions in their group."


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'submission', 'assigned', 'score')
    search_fields = ('submission__student__lastname', 'submission__student__firstname', 'submission__student__username', 'submission__student__group_id')
    list_filter = ('assigned__username',)
    actions = ['permit_ta', 'permit_superta']

    def permit_ta(self, request, queryset):
        permit_instructions = 0
        reviews_count = 0

        for review in queryset:
            reviews_count += 1

            student_groupid = review.submission.student.group_id
            ta = Student.objects.filter(group_id=student_groupid, usertype="ta")
            if len(ta) == 0:
                self.message_user(request, "Could not find TA for %s in group %d." % (review.submission.student, student_groupid), level=messages.WARNING)

            ## If this review is assigned to the TA, skip
            if review.assigned == ta:
                continue

            ## Add permits. Don't add duplicate permits.
            permit = Permission.objects.get_or_create(review=review)
            new_permits = set((ta)) - set(permit[0].student.all())
            for n in new_permits:
                permit[0].student.add(n)
                permit_instructions += 1

        self.message_user(request, "Needed to add %s permits for %s reviews." % (str(permit_instructions), str(reviews_count)) )

    permit_ta.short_description = "Find and Permit assigned TA to participate"

    def permit_superta(self, request, queryset):
        superta = Student.objects.filter(usertype="superta")
        permit_instructions = 0
        reviews_count = 0
        self.message_user(request, "Found %s Super TAs." % str(len(superta)) )
        for review in queryset:
            reviews_count += 1
            permit = Permission.objects.get_or_create(review=review)
            new_permits = set((superta)) - set(permit[0].student.all())
            for n in new_permits:
                permit[0].student.add(n)
                permit_instructions += 1

        self.message_user(request, "Needed to add %s permits for %s reviews." % (str(permit_instructions), str(reviews_count)) )

    permit_superta.short_description = "Permit all Super TAs to participate"


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review',)
    list_filter = ('review__submission__student__username',)
    filter_horizontal = ('student',)


class ReviewConvoAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'text')
    search_fields = ('student__username', 'student__firstname', 'student__lastname', 'review__submission__student__username',
                'review__submission__student__firstname', 'review__submission__student__lastname')
    list_filter = ('review',)


# Form Views
class ReviewConvoForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'style': 'width:90%'}))
    field = ('text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('score')

class ReportForm(forms.Form):
    file_name = forms.CharField(max_length=100)
    file_link = forms.CharField(max_length=1000)
    fields = ('file_name', 'file_link')
