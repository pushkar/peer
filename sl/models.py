from django.db import models
from django import forms
from django.contrib import admin
from django.forms.widgets import RadioSelect

class StudentInfo(models.Model):
	userid = models.CharField(max_length=50)
	gtpe_finished = models.IntegerField()
	score = models.IntegerField()

class StudentInfoAdmin(admin.ModelAdmin):
	list_display = ('id', 'userid', 'score')
	list_filter = ('gtpe_finished',)

class Question(models.Model):
	type = models.CharField(max_length=20)
	question = models.CharField(max_length=2000)

	def __unicode__(self):
		return self.question

class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'type', 'question')
	search_fields = ('question',)
	ordering = ('id',)

class Answer(models.Model):
	question_id = models.IntegerField()
	student_id = models.IntegerField()
	answer = models.CharField(max_length=2000)
	answer_tf = models.CharField(max_length=10)
	score = models.FloatField(default=0.0)
	count = models.IntegerField(default=1)

	def __unicode__(self):
		return 'Answer to Q' + str(self.question_id)

class AnswerAdmin(admin.ModelAdmin):
	list_display = ('id', 'question_id', 'answer_tf', 'answer')
	list_filter = ('question_id', 'student_id')

class Log(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	student_id = models.IntegerField()
	question_id = models.IntegerField()
	type_of_question = models.CharField(max_length=10)
	log_id = models.IntegerField()

	def __unicode__(self):
		return str(self.created)

	class Meta:
		get_latest_by = "created"

class LogAdmin(admin.ModelAdmin):
	list_display = ('id', 'created', 'type_of_question', 'log_id')
	ordering = ('-created',)
	list_filter = ('type_of_question', 'created', 'student_id', 'question_id')


class TFForm(forms.Form):
	answer_tf = forms.ChoiceField(
			widget=RadioSelect(),
			choices=[['1','True'],['0','False']])
	answer = forms.CharField(widget=forms.Textarea)
	fields = ('answer', 'explanation')

class TFLog(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	student_id = models.IntegerField()
	question_id = models.IntegerField()
	answer_tf = models.CharField(max_length=10)
	answer = models.CharField(max_length=2000)
	score = models.FloatField(default=0.0)

	def __unicode__(self):
		return str(self.created)

class TFLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'created', 'question_id', 'answer_tf', 'answer', 'score')
	ordering = ('-created',)
	list_filter = ('question_id', 'created',)

class MCForm(forms.Form):
	choice = forms.ChoiceField(
			widget=RadioSelect(),
			choices=[['1','First is True'],
					['2','Second is True'],
					['3', 'Both are True'],
					['4', 'Both are False']])

class MCLog(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	student_id = models.IntegerField()
	question_id = models.IntegerField()
	answer1_id = models.IntegerField()
	answer2_id = models.IntegerField()
	choice = models.IntegerField()
	score = models.FloatField(default=0.0)

	def __unicode__(self):
		return str(self.created)

class MCLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'created', 'question_id', 'answer1_id', 'answer2_id', 'choice', 'score')
	ordering = ('-created',)
	list_filter = ('question_id', 'created',)
