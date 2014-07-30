from django.db import models
from django import forms
from django.forms.widgets import RadioSelect

class Student(models.Model):
	email = models.CharField(max_length=50)

	def __unicode__(self):
		return self.email

class Question(models.Model):
	text = models.CharField(max_length=500)

	def __unicode__(self):
		return self.text

class Answer(models.Model):
	question_id = models.IntegerField()
	student_id = models.IntegerField()
	answer = models.CharField(max_length=500)
	answer_tf = models.CharField(max_length=20)
	score = models.FloatField(default=0.0)

	def __unicode__(self):
		return str(self.student_id) + "'s answer to q" + str(self.question_id)

class ExamForm(forms.Form):
	student_id = forms.IntegerField()
	question_id = forms.IntegerField()
	answer = forms.CharField(required=True)
	answer_tf = forms.ChoiceField(
			widget=RadioSelect(),
			choices=[['1','True'],['0','False']])
	fields = ('student_id', 'question_id', 'answer')


class Score(models.Model):
	answer_id = models.IntegerField()
	scorer_id = models.IntegerField()
	score = models.IntegerField()

	def __unicode__(self):
		return str(self.scorer_id) + "'s score for a" + str(self.answer_id)
