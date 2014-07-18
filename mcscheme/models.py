from django.db import models

class Student(models.Model):
	email = models.CharField(max_length=50, primary_key=True)

	def __unicode__(self):
		return self.email

class Question(models.Model):
	text = models.CharField(max_length=500)

	def __unicode__(self):
		return self.text

class Answer(models.Model):
	question_id = models.IntegerField()
	student_id = models.IntegerField()
	text = models.CharField(max_length=500)
	score = models.FloatField(default=0.0)

	def __unicode__(self):
		return str(self.student_id) + "'s answer to q" + str(self.question_id)

class Score(models.Model):
	answer_id = models.IntegerField()
	scorer_id = models.IntegerField()
	score = models.IntegerField()

	def __unicode__(self):
		return str(self.scorer_id) + "'s score for a" + str(self.answer_id)
