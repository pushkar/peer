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

    class Meta:
        ordering = ['pk']

class Submission(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    files = models.CharField(max_length=15000)

    def __unicode__(self):
        return unicode(unicode(self.student) + ", " + unicode(self.assignment))

# Each Review is assigned to someone and has a score
class Review(models.Model):
    submission = models.ForeignKey(Submission)
    assigned = models.ForeignKey(Student)
    score = models.CharField(max_length=10, null=True, blank=True)
    details = models.CharField(default=None, max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return unicode(unicode(self.submission.student) + " - R" + unicode(self.pk) + ", " + unicode(self.submission.assignment))

# Who can access the review other than the one who it was assigned to?
class Permission(models.Model):
    student = models.ForeignKey(Student)
    review = models.ManyToManyField(Review)

    def __unicode__(self):
        return unicode(unicode(self.student) + " Permissions ")

class ReviewConvo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review)
    student = models.ForeignKey(Student)
    text =  models.CharField(max_length=10000, null=True, blank=True)
    score = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ['created']
        get_latest_by = ['created']


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date')

class AssignmentPageAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'name', 'title')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'student', 'assignment', 'files')
    search_fields = ('student__lastname', 'student__firstname', 'student__username')
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
            a_name = submission.assignment.short_name
            ## Check if they have opted in
            if submission.student not in reviewers_all:
                reviewers_all.discard(submission.student)
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
                reviewers.discard(submission.student)

            ## Remove reviewers who haven't submitted an assignment
            reviewers_nosub = set()
            for r in reviewers:
                if Submission.objects.filter(student=r, assignment__short_name=a_name).count() <= 0:
                    reviewers_nosub.add(r)
            reviewers -= reviewers_nosub

            ## Remove all reviewers who have been assigned 3 reviews
            reviewers_assigned = set()
            for r in reviewers:
                if Review.objects.filter(assigned=r, submission__assignment__short_name=a_name).count() >= 3:
                    reviewers_assigned.add(r)

            reviewers -= reviewers_assigned

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
    list_filter = ('submission__assignment__name', 'assigned__usertype', )
    actions = ['remove_zero_convos','permit_ta', 'permit_superta']

    def remove_zero_convos(self, request, queryset):
        del_count = 0

        for review in queryset:
            count = ReviewConvo.objects.filter(review=review).count()
            if count == 0:
                review.delete()
                del_count += 1

        self.message_user(request, "Needed to delete %s reviews." % (str(del_count)) )

    remove_zero_convos.short_description = "Remove Reviews with no convos"

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
    list_display = ('pk', 'student',)
    list_filter = ('review',)
    filter_horizontal = ('review',)


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
