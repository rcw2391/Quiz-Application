from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('login', views.user_login, name='user_login'),
    path('register', views.user_register, name='user_register'),
    path('logout', views.user_logout, name='user_logout'),
    path('new_quiz', views.new_quiz, name='new_quiz'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('edit/<str:quiz_id>', views.edit_quiz, name='edit_quiz'),
    path('add_question/<str:quiz_id>', views.add_question, name='add_question'),
    path('delete_question/<str:quiz_id>', views.delete_question, name='delete_question'),
    path('edit_question_main/<str:quiz_id>', views.edit_question_main, name='edit_question_main'),
    path('edit_question/<str:question_id>', views.edit_question, name='edit_question'),
    path('delete_quiz/<str:quiz_id>', views.delete_quiz, name="delete_quiz"),
    path('user_list_information/<str:quiz_id>', views.user_list_information, name="user_list_information"),
    path('add_user_to_quiz/<str:quiz_id>', views.add_user_to_quiz, name="add_user_to_quiz"),
    path('take_quiz/<str:quiz_id>', views.take_quiz, name="take_quiz"),
    path('begin_quiz/<str:quiz_id>', views.begin_quiz, name='begin_quiz'),
    path('view_submissions/<str:quiz_id>/<str:user_id>', views.view_submissions, name='view_submissions')
]