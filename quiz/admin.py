from django.contrib import admin
from .models import UserProfile, Quiz, Question, CorrectAnswer, IncorrectAnswer, Score, AnsweredQuestion

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(CorrectAnswer)
admin.site.register(IncorrectAnswer)
admin.site.register(Score)
admin.site.register(AnsweredQuestion)