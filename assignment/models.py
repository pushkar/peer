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
    content = models.TextField(max_length=5000)

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


# Admin Views
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'due_date')
    actions = ['populate_submissions']

    def populate_submissions(self, request, queryset):
        files_count = 0
        files_total = 0
        submissions_count = 0

        for a in queryset:
            try:
                g = Global.objects.get(key="submissions")
                submission_str = urllib2.urlopen(g.value).read()
                reader = csv.reader(submission_str.split('\n'), delimiter=',')
                for row in reader:
                    files_total = files_total + 1
                    s = Student.objects.get(username=row[0])
                    if s:
                        submission = Submission.objects.get_or_create(student=s, assignment=a)
                        file = SubmissionFile.objects.get_or_create(submission=submission[0], name=row[1], link=row[2])
                        if submission[1]:
                            submissions_count += 1
                        if file[1]:
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
    list_display = ('student', 'assignment')
    search_fields = ('student__lastname', 'student__firstname', 'student__username', 'student__group_id')
    actions = ['assign_reviewers']

    def assign_reviewers(self, request, queryset):
        submission_count = len(queryset)
        reviewer_count = 0

        for submission in queryset:
            try:
                opt = OptIn.objects.get(student=submission.student)
                self.message_user(request, "%s hasn't opted in yet." % (str(submission.student)), level=messages.WARNING)
            except:
                student_groupid = submission.student.group_id
                group = Student.objects.filter(submission__student__group_id=student_groupid, usertype='student')
                if len(group) == 0:
                    self.message_user(request, "Group size %s is too small." % str(len(group)))
                else:
                    reviewers_assigned = len(Review.objects.filter(submission=submission))
                    tries = 0
                    while reviewers_assigned <= 3:
                        # Break if you don't find anyone
                        tries += 1
                        if tries > len(group)-1:
                            self.message_user(request, "Cound not find anyone for %s." % (str(submission.student)), level=messages.WARNING )
                            break

                        # Keep randomly finding someone
                        reviewer = random.choice(group)
                        # If the reviewer is same as the submitter
                        if reviewer.username == submission.student.username:
                            continue

                        # If the reviewer already has 3 submissions
                        reviews = Review.objects.filter(assigned=reviewer)
                        if len(reviews) < 3:
                            review = Review.objects.get_or_create(submission=submission, assigned=reviewer, score="0.0")
                            reviewers_assigned += 1
                            if review[1]:
                                reviewer_count += 1

        self.message_user(request, "Assigned %s reviewers to %s submissions." % (str(reviewer_count), str(submission_count)) )

    assign_reviewers.short_description = "Assign 3 Reviewers"

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'assigned', 'score')
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
            #else:
            #    self.message_user(request, "Found TA %s." % ta)

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
    list_display = ('review',)
    list_filter = ('review__submission__student__username',)
    filter_horizontal = ('student',)


class ReviewConvoAdmin(admin.ModelAdmin):
    list_display = ('created', 'student', 'text')
    search_fields = ('text',)


# Form Views
class ReviewConvoForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'style': 'width:90%'}))
    field = ('text')

class ScoreForm(forms.Form):
    review_score = forms.ChoiceField(choices=[(x, x) for x in range(1, 6)])
    field = ('score')

class ReportForm(forms.Form):
    report_link = forms.CharField(max_length=100)
    fields = ('link')
