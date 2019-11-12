from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Quiz(models.Model):
    users = models.ManyToManyField(UserProfile)
    name = models.CharField(max_length=20)
    quiz_owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    is_repeatable = models.BooleanField()
    time_limit = models.IntegerField()

    class Meta:
        unique_together = ['name', 'quiz_owner']
    
    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.CharField(max_length=155)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.text

class CorrectAnswer(models.Model):
    text = models.CharField(max_length=155)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        ordering = ['text']

    def __str__(self):
        return self.text

class IncorrectAnswer(models.Model):
    text = models.CharField(max_length=155)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        ordering = ['text']

    def __str__(self):
        return self.text

class Score(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    expiration_date = models.DateTimeField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.score)

class AnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct_answers_selected = models.ManyToManyField(CorrectAnswer, blank=True)
    incorrect_answers_selected = models.ManyToManyField(IncorrectAnswer, blank=True)
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    is_correct = models.BooleanField()

    def __str__(self):
        return self.question.text