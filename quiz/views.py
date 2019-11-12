from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from .models import UserProfile, Quiz, Question, CorrectAnswer, IncorrectAnswer, Score, AnsweredQuestion
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone
from random import shuffle

# Create your views here.
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(username=form.cleaned_data['username'])
            if User.objects.filter(username=user.username):
                return render(request, 'quiz/register.html', {'form': form, 'is_logged_in': request.user.is_authenticated, 
                                'isError': True, 'error': 'Username already exists!', 'isActive': 'register'})
            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                return render(request, 'quiz/register.html', {'form': form, 'is_logged_in': request.user.is_authenticated, 
                                'isError': True, 'error': 'Passwords do not match!', 'isActive': 'register'})
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = UserProfile()
            profile.user = user
            profile.save()
            return HttpResponseRedirect('../')

    form = RegisterForm()
    return render(request, 'quiz/register.html', {'form': form, 'is_logged_in': request.user.is_authenticated, 'isActive': 'register'})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                request.session['is_logged_in'] = True
                return HttpResponseRedirect('/quiz/dashboard')
            else:
                return render(request, 'quiz/login.html', {'form': form, 'is_logged_in': request.user.is_authenticated, 'isActive': 'login',
                                                            'isError': True, 'error': 'Invalid Username/Password, please try again.'})
            return HttpResponseRedirect('../')
    form = LoginForm()
    return render(request, 'quiz/login.html', {'form': form, 'is_logged_in': request.user.is_authenticated, 'isActive': 'login'})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('../')

@login_required
def new_quiz(request):
    if request.method == 'POST':
        name = request.POST['name_input']
        quiz_owner = request.user.userprofile
        time_limit = int(request.POST['time_limit_input'])
        try:
            Quiz.objects.get(quiz_owner=quiz_owner, name=name)
        except Exception:
            pass
        else:
            return render(request, 'quiz/new_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'new_quiz', 
                                                            'name_value': name, 'isError': True, 'error': 'Quiz name already exists.',
                                                            'time_limit': time_limit})
        if time_limit > 120 or time_limit < 0:
            return render(request, 'quiz/new_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'new_quiz', 
                                                        'name_value': name, 'isError': True, 'error': 'Time limit must be between 0 and 120 inclusive.',
                                                        'time_limit': time_limit})
        if request.POST['is_repeatable'] == '0':
            is_repeatable = False
        else:
            is_repeatable = True
        quiz = Quiz(name=name, is_repeatable=is_repeatable, quiz_owner=quiz_owner, time_limit=time_limit)
        quiz.save()
        return HttpResponseRedirect('/quiz/dashboard')   
    return render(request, 'quiz/new_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'new_quiz', 'name_value': '',
                                                    'time_limit': 0})

@login_required
def dashboard(request):
    quiz_owner = request.user.userprofile
    detailed_quiz_member_list = []
    try:
        quiz_owner_list = list(Quiz.objects.filter(quiz_owner=quiz_owner))
    except Exception:
        quiz_owner_list = []
    try:
        quiz_member_list = list(Quiz.objects.filter(users=quiz_owner))
        print(quiz_member_list)
    except Exception:
        quiz_member_list = []
    for quiz in quiz_member_list:
        score_list = []
        score_recent = list(Score.objects.filter(quiz=quiz, user=request.user.userprofile).order_by('-created_date'))
        for score in score_recent:
            score_list.append(score.score)
        score_best = score_list.sort(reverse=True)
        if len(score_recent) == 0:
            score_recent = 'None'
            score_best = 'None'
            if quiz.quiz_owner != None:
                can_take_quiz = True
            else:
                can_take_quiz = False
        else:
            score_recent = score_recent[0].score
            score_best = score_list[0]
            if quiz.quiz_owner != None:
                can_take_quiz = quiz.is_repeatable
            else:
                can_take_quiz = False
        detailed_quiz_member_list.append({'quiz': quiz, 'score_recent': score_recent, 'score_best': score_best, 
                                                'can_take_quiz': can_take_quiz}) 
    return render(request, 'quiz/dashboard.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
                                                    'quiz_owner_list': quiz_owner_list, 'quiz_owner_list_len': len(quiz_owner_list),
                                                    'username': request.user.username, 'detailed_quiz_member_list': detailed_quiz_member_list,
                                                    'quiz_member_list_len': len(quiz_member_list), 'user_id': request.user.userprofile.id})

@login_required
def edit_quiz(request, quiz_id):
    if request.method == 'POST':
        try:
            quiz = Quiz.objects.get(name=quiz_id, quiz_owner=request.user.userprofile)
        except:
            return HttpResponseRedirect('/quiz/dashboard')
        if request.POST['action_dropdown'] == 'nothing':
            return HttpResponseRedirect('/quiz/dashboard')
        if request.POST['action_dropdown'] == 'change_name':
            new_name = request.POST['quiz_name']
            try:
                Quiz.objects.get(name=new_name, quiz_owner=request.user.userprofile)
            except:
                quiz.name = new_name
                quiz.save()
                return HttpResponseRedirect('/quiz/edit/' + quiz.name)
            else:
                quiz.name = new_name
                return render(request, 'quiz/edit_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                'quiz': quiz, 'isError': True, 'error': 'You are already using this quiz name.'})
        if request.POST['action_dropdown'] == 'add_question':
            return HttpResponseRedirect('/quiz/add_question/' + quiz.name)
        
        if request.POST['action_dropdown'] == 'delete_question':
            return HttpResponseRedirect('/quiz/delete_question/' + quiz.name)
        
        if request.POST['action_dropdown'] == 'edit_question':
            return HttpResponseRedirect('/quiz/edit_question_main/' + quiz.name)
        if request.POST['action_dropdown'] == 'delete_quiz':
            return render(request, 'quiz/delete_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                                'quiz': quiz})
        if request.POST['action_dropdown'] == 'change_time_limit':
            time_limit = int(request.POST['time_limit_input'])
            if time_limit < 0 or time_limit > 120:
                return render(request, 'quiz/edit_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                'quiz': quiz, 'isError': True, 'error': 'Time limit must be between 0 and 120 inclusive.'})
        
            else:
                quiz.time_limit = time_limit
                quiz.save()
                return HttpResponseRedirect('/quiz/edit/' + quiz_id)
        if request.POST['action_dropdown'] == 'change_repeatable':
            try:
                request.POST['is_repeatable_input']
            except Exception:
                quiz.is_repeatable = False
                quiz.save()
            else:
                quiz.is_repeatable = True
                quiz.save()
        return HttpResponseRedirect('/quiz/edit/' + quiz_id)
    
    quiz_owner = request.user.userprofile
    try:
        quiz = Quiz.objects.get(name=quiz_id, quiz_owner=quiz_owner)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    return render(request, 'quiz/edit_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz})

@login_required
def add_question(request, quiz_id):
    quiz_owner = request.user.userprofile
    try:
        quiz = Quiz.objects.get(name=quiz_id, quiz_owner=quiz_owner)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if request.method == 'POST':        
        text = request.POST['question_input']
        # Input Validation: Question cannot be duplicate or empty.
        number_of_answers = int(request.POST['number_of_answers_input'])
        number_of_correct_answers = int(request.POST['number_of_correct_answers_input'])
        number_of_incorrect_answers = number_of_answers - number_of_correct_answers
        correct_answers = []
        incorrect_answers = []
        for answer in range(number_of_correct_answers):
            correct_answers.append(request.POST['correct_answer'+str(answer)])
        for answer in range(number_of_incorrect_answers):
            incorrect_answers.append(request.POST['incorrect_answer'+str(answer)])
        try:
            question = Question.objects.get(text=text, quiz=quiz)
        except:
            question = Question(text=text, quiz=quiz)
        else:
            isError = True
            error = 'This question already exists'
            return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isError': isError, 'error': error, 'question_text': question.text,
                                                    'number_of_answers': number_of_answers, 'number_of_correct_answers': number_of_correct_answers,
                                                    'number_of_incorrect_answers': number_of_incorrect_answers, 'correct_answers': correct_answers,
                                                    'incorrect_answers': incorrect_answers, 'is_submitted': True})
        if len(question.text) < 1:
            isError = True
            error = 'Question cannot be empty.'
            return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isError': isError, 'error': error, 'question_text': question.text,
                                                    'number_of_answers': number_of_answers, 'number_of_correct_answers': number_of_correct_answers,
                                                    'number_of_incorrect_answers': number_of_incorrect_answers, 'correct_answers': correct_answers,
                                                    'incorrect_answers': incorrect_answers, 'is_submitted': True})
        # Input Validation: At least 1 correct answer, and answers must have text.
        if number_of_correct_answers < 1:
            isError = True
            error = 'You must have at least one correct answer.'
            return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isError': isError, 'error': error, 'question_text': question.text,
                                                    'number_of_answers': number_of_answers, 'number_of_correct_answers': number_of_correct_answers,
                                                    'number_of_incorrect_answers': number_of_incorrect_answers, 'correct_answers': correct_answers,
                                                    'incorrect_answers': incorrect_answers, 'is_submitted': True})
        for answer in range(number_of_correct_answers):
            if len(request.POST['correct_answer'+str(answer)]) < 1:
                isError = True
                error = 'Answers cannot be empty.'
                return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isError': isError, 'error': error, 'question_text': question.text,
                                                    'number_of_answers': number_of_answers, 'number_of_correct_answers': number_of_correct_answers,
                                                    'number_of_incorrect_answers': number_of_incorrect_answers, 'correct_answers': correct_answers,
                                                    'incorrect_answers': incorrect_answers, 'is_submitted': True})
        for answer in range(number_of_incorrect_answers):
            if len(request.POST['incorrect_answer'+str(answer)]) < 1:
                isError = True
                error = 'Answers cannot be empty.'
                return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isError': isError, 'error': error, 'question_text': question.text,
                                                    'number_of_answers': number_of_answers, 'number_of_correct_answers': number_of_correct_answers,
                                                    'number_of_incorrect_answers': number_of_incorrect_answers, 'correct_answers': correct_answers,
                                                    'incorrect_answers': incorrect_answers, 'is_submitted': True})
        question.save()
        for answer in range(number_of_correct_answers):
            text = request.POST['correct_answer'+ str(answer)]
            correct_answer = CorrectAnswer(text=text, question=question)
            correct_answer.save()
            
        for answer in range(number_of_incorrect_answers):
            text = request.POST['incorrect_answer'+ str(answer)]
            incorrect_answer = IncorrectAnswer(text=text, question=question)
            incorrect_answer.save()
        return render(request, 'quiz/edit_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'isSuccess': True, 'success': 'Question successfully added.'})
    
    return render(request, 'quiz/add_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                    'quiz': quiz, 'question_text': '', 'number_of_answers': 0, 
                                                    'number_of_correct_answers': 0, 'number_of_incorrect_answers': 0, 
                                                    'correct_answers': [], 'incorrect_answers': [], 'is_submitted': False})

@login_required
def delete_question(request, quiz_id):
    if request.method == 'POST':
        for question_number in range(0, len(request.POST) - 1):
            question_id = request.POST['question'+str(question_number)]
            question = Question.objects.get(id=question_id)
            if AnsweredQuestion.objects.filter(question=question).count() > 0:
                question.quiz = None
                question.save()
            else:
                question.delete()
            
        print('Question deleted')
        return HttpResponseRedirect('/quiz/delete_question/'+quiz_id)
    
    try:
        quiz = Quiz.objects.get(name=quiz_id, quiz_owner=request.user.userprofile)
    except:
        return HttpResponseRedirect('/quiz/dashboard')
    question_list = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz/delete_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_quiz',
                                                        'question_list': question_list, 'quiz': quiz})

@login_required
def edit_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        quiz = question.quiz
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    try:
        user = request.user.userprofile
    except Exception:
        user = None
    if quiz.quiz_owner != user:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        question_text = question.text
        correct_answer_list = CorrectAnswer.objects.filter(question=question)
        incorrect_answer_list = IncorrectAnswer.objects.filter(question=question)
        # Set defaults for edit validation - Delete/Change has No checked
        change_correct_answers_list = []
        change_incorrect_answers_list = []
        for item in correct_answer_list:
            change_correct_answers_list.append({'answer': item, 'change': 0})
        for item in incorrect_answer_list:
            change_incorrect_answers_list.append({'answer': item, 'change': 0})
        return render(request, 'quiz/edit_question_answers.html', {'is_logged_in': request.user.is_authenticated, 
                                                                    'isActive': 'edit_question',
                                                                    'question': question_text,
                                                                    'question_id': question_id,
                                                                    'quiz': quiz,
                                                                    'is_new': False,
                                                                    'change_correct_answers_list': change_correct_answers_list,
                                                                    'change_incorrect_answers_list': change_incorrect_answers_list})

    if request.method == 'POST':
        is_answer_error = False
        answer_error = ''
        try:
            number_of_new_answers = int(request.POST['number_of_new_answers_input'])
        except Exception:
            number_of_new_answers = 0
        question_text = request.POST['question_text']
        # Question input validation:
        # Questions cannot be duplicated
        try:
            Question.objects.get(text=question_text)
        except:
            is_question_error = False
            question_error = ''
        else:
            if question.text == question_text:
                is_question_error = False
                question_error = ''
            else:
                is_question_error = True
                question_error = 'Question must be unique.'
        if len(question_text) == 0:
            is_question_error = True
            question_error = 'Question must not be empty.'
        correct_answers_list = CorrectAnswer.objects.filter(question=question)
        incorrect_answers_list = IncorrectAnswer.objects.filter(question=question)
        number_of_correct_answers = len(correct_answers_list)
        number_of_incorrect_answers = len(incorrect_answers_list)
        print(len(correct_answers_list), ' correct answers')
        print(len(incorrect_answers_list), ' incorrect answers')
        # Answer input validation: 
        # There must be at least one correct answer
        # There can only be 9 questions total
        change_correct_answers_list = []
        change_incorrect_answers_list = []
        # Verify there is at least one correct answer
        for number in range(len(correct_answers_list)):
            if request.POST['change_correct_answer'+str(number)] != '1' and request.POST['delete_correct_answer'+str(number)] != '1':
                is_correct_answer = True
                break
            else:
                is_correct_answer = False
        # Adjust number of answers total based on convert/delete
        for number in range(len(correct_answers_list)):
            # Validate correct answer is not empty
            correct_answers_list[number].text = request.POST['correct_answer'+str(number)]
            if len(correct_answers_list[number].text) == 0:
                is_answer_error = True
                answer_error = 'Answers must not be empty.'
            if request.POST['change_correct_answer'+str(number)] == '1' and request.POST['delete_correct_answer'+str(number)] == '0':
                number_of_correct_answers -= 1
                number_of_incorrect_answers += 1
                change_correct_answers_list.append({'answer': correct_answers_list[number], 'change': 1})
            elif request.POST['delete_correct_answer'+str(number)] == '1':
                number_of_correct_answers -= 1
                change_correct_answers_list.append({'answer': correct_answers_list[number], 'change': 2})
            else:
                change_correct_answers_list.append({'answer': correct_answers_list[number], 'change': 0})
        for number in range(len(incorrect_answers_list)):
            # Validate incorrect answer is not empty
            incorrect_answers_list[number].text = request.POST['incorrect_answer'+str(number)]
            if len(incorrect_answers_list[number].text) == 0:
                is_answer_error = True
                answer_error = 'Answers must not be empty.'
            if request.POST['change_incorrect_answer'+str(number)] == '1' and request.POST['delete_incorrect_answer'+str(number)] == '0':
                number_of_incorrect_answers -= 1
                number_of_correct_answers += 1
                change_incorrect_answers_list.append({'answer': incorrect_answers_list[number], 'change': 1})
            elif request.POST['delete_incorrect_answer'+str(number)] == '1':
                number_of_incorrect_answers -= 1
                change_incorrect_answers_list.append({'answer': incorrect_answers_list[number], 'change': 2})
            else:
                change_incorrect_answers_list.append({'answer': incorrect_answers_list[number], 'change': 0})
        if not is_correct_answer:
            for number in range(len(incorrect_answers_list)):
                if request.POST['change_incorrect_answer'+str(number)] != '0' and request.POST['delete_incorrect_answer'+str(number)] != '1':
                    is_correct_answer = True
                    break
                else:
                    is_correct_answer = False
        # Save updated text
        for number in range(len(correct_answers_list)):
            correct_answers_list[number].text = request.POST['correct_answer'+str(number)]
        for number in range(len(incorrect_answers_list)):
            incorrect_answers_list[number].text = request.POST['incorrect_answer'+str(number)]
        if (not is_correct_answer) and number_of_new_answers == 0:
            is_correct_answer_error = True
            correct_answer_error = 'A question must have at least one correct answer.'
            return render(request, 'quiz/edit_question_answers.html', {'is_logged_in': request.user.is_authenticated, 
                                                                    'isActive': 'edit_question',
                                                                    'question': question_text,
                                                                    'question_id': question_id,
                                                                    'quiz': quiz,
                                                                    'is_correct_answer_error': is_correct_answer_error,
                                                                    'correct_answer_error': correct_answer_error,
                                                                    'is_question_error': is_question_error,
                                                                    'question_error': question_error,
                                                                    'change_correct_answers_list': change_correct_answers_list,
                                                                    'change_incorrect_answers_list': change_incorrect_answers_list,
                                                                    'is_new': False,
                                                                    'is_answer_error': is_answer_error,
                                                                    'answer_error': answer_error})
        # More than 9 Answers                                                           
        elif not is_correct_answer and  number_of_new_answers != 0:
            if number_of_correct_answers + number_of_incorrect_answers + number_of_new_answers > 9:
                is_too_many_answers = True
                too_many_answers_error = 'You cannot have more than 9 answers for a question.'
            else:
                is_too_many_answers = False
                too_many_answers_error = ''
            incorrect_new_answers_list = []
            correct_new_answers_list = []
            for number in range(number_of_new_answers):
                text = request.POST['new_answer'+str(number)]
                try:
                    request.POST['new_answer_checkbox'+str(number)]
                except Exception:
                    incorrect_new_answers_list.append(IncorrectAnswer(text=text, question=question))
                else:
                    is_correct_answer = True
                    correct_new_answers_list.append(CorrectAnswer(text=text, question=question))
            if not is_correct_answer:
                is_correct_answer_error = True
                correct_answer_error = 'A question must have at least one correct answer.'
                print(change_correct_answers_list)
                print(change_incorrect_answers_list)
                return render(request, 'quiz/edit_question_answers.html', {'is_logged_in': request.user.is_authenticated, 
                                                                    'isActive': 'edit_question',
                                                                    'question': question_text,
                                                                    'question_id': question_id,
                                                                    'quiz': quiz,
                                                                    'is_correct_answer_error': is_correct_answer_error,
                                                                    'correct_answer_error': correct_answer_error,
                                                                    'is_question_error': is_question_error,
                                                                    'question_error': question_error,
                                                                    'is_too_many_answers': is_too_many_answers,
                                                                    'too_many_answers_error': too_many_answers_error,
                                                                    'incorrect_new_answers_list': incorrect_new_answers_list,
                                                                    'correct_new_answers_list': correct_new_answers_list,
                                                                    'change_correct_answers_list': change_correct_answers_list,
                                                                    'change_incorrect_answers_list': change_incorrect_answers_list,
                                                                    'is_new': True,
                                                                    'number_of_new_answers': number_of_new_answers,
                                                                    'is_answer_error': is_answer_error,
                                                                    'answer_error': answer_error})
            elif is_too_many_answers or is_answer_error:
                return render(request, 'quiz/edit_question_answers.html', {'is_logged_in': request.user.is_authenticated, 
                                                                    'isActive': 'edit_question',
                                                                    'question': question_text,
                                                                    'question_id': question_id,
                                                                    'quiz': quiz,
                                                                    'is_question_error': is_question_error,
                                                                    'question_error': question_error,
                                                                    'is_too_many_answers': is_too_many_answers,
                                                                    'too_many_answers_error': too_many_answers_error,
                                                                    'incorrect_new_answers_list': incorrect_new_answers_list,
                                                                    'correct_new_answers_list': correct_new_answers_list,
                                                                    'change_correct_answers_list': change_correct_answers_list,
                                                                    'change_incorrect_answers_list': change_incorrect_answers_list,
                                                                    'is_new': True,
                                                                    'number_of_new_answers': number_of_new_answers,
                                                                    'is_answer_error': is_answer_error,
                                                                    'answer_error': answer_error})   
        # Save Correct and Incorrect Answers
        # Check if quiz has been taken with this question.
        if AnsweredQuestion.objects.filter(question=question).count() > 0:
            make_new_question = True
            question.quiz = None
            question.save()
            question = Question(text=question_text, quiz=quiz)
            question.save()
        else:
            make_new_question = False
            question.text = question_text
            question.save()
        for number in range(len(correct_answers_list)):
            if  request.POST['change_correct_answer'+str(number)] == '1' or request.POST['delete_correct_answer'+str(number)] == '1':
                if not make_new_question:
                    correct_answers_list[number].delete()
            if request.POST['delete_correct_answer'+str(number)] != '1' and request.POST['change_correct_answer'+str(number)] == '1':
                text = request.POST['correct_answer'+str(number)]
                new_incorrect_answer = IncorrectAnswer(text=text, question=question)
                new_incorrect_answer.save()
            else:
                text = request.POST['correct_answer'+str(number)]
                if not make_new_question:
                    correct_answers_list[number].text = text
                    correct_answers_list[number].save()
                else:
                    new_correct_answer = CorrectAnswer(text=text, question=question)
                    new_correct_answer.save()
        for number in range(len(incorrect_answers_list)):
            if  request.POST['change_incorrect_answer'+str(number)] == '1' or request.POST['delete_incorrect_answer'+str(number)] == '1':
                if not make_new_question:
                    incorrect_answers_list[number].delete()
            if request.POST['delete_incorrect_answer'+str(number)] != '1' and request.POST['change_incorrect_answer'+str(number)] == '1':
                text = request.POST['incorrect_answer'+str(number)]
                new_correct_answer = CorrectAnswer(text=text, question=question)
                new_correct_answer.save()
            else:
                text = request.POST['incorrect_answer'+str(number)]
                if not make_new_question:
                    incorrect_answers_list[number].text = text
                    incorrect_answers_list[number].save()
                else:
                    new_incorrect_answer = IncorrectAnswer(text=text, question=question)
                    new_incorrect_answer.save()
        # Save new answers
        for number in range(number_of_new_answers):
            text = request.POST['new_answer'+str(number)]
            try:
                request.POST['new_answer_checkbox'+str(number)]
            except Exception:
                new_answer = IncorrectAnswer(text=text, question=question)
                new_answer.save()
            else:
                new_answer = CorrectAnswer(text=text, question=question)
                new_answer.save()
        question_list = Question.objects.filter(quiz=quiz)
        return render(request, 'quiz/edit_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_question',
                                                        'question_list': question_list, 'quiz': quiz,
                                                        'successful_edit': 'Question updated successfully.',
                                                        'is_successful_edit': True})

@login_required
def edit_question_main(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if quiz.quiz_owner != request.user.userprofile:
            return HttpResponseRedirect('/quiz/dashboard')
    question_list = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz/edit_question.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'edit_question',
                                                        'question_list': question_list, 'quiz': quiz})

@login_required
def delete_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if quiz.quiz_owner != request.user.userprofile:
            return HttpResponseRedirect('/quiz/dashboard')    
    if request.method == 'POST':
        if 'DELETE' != request.POST['delete_quiz_input']:
            return render(request, 'quiz/delete_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'delete_quiz',
                                                            'quiz': quiz, 'isError': True, 'error': 'Entry does not match.'})
        else:
            if Score.objects.filter(quiz=quiz).count() > 0:
                quiz.quiz_owner = None
                quiz.save()
            else:
                quiz.delete()
            return HttpResponseRedirect('/quiz/dashboard')

@login_required
def user_list_information(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if quiz.quiz_owner != request.user.userprofile:
            return HttpResponseRedirect('/quiz/dashboard')
    quiz_users = quiz.users.all()
    quiz_user_len = len(quiz_users)
    return render(request, 'quiz/user_list_information.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
                                                                'quiz': quiz, 'quiz_user_len': quiz_user_len, 'quiz_users': quiz_users})
                                                            
@login_required
def add_user_to_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id, quiz_owner=request.user.userprofile)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if quiz.quiz_owner != request.user.userprofile:
            return HttpResponseRedirect('/') 
    if request.method == 'GET':
        return render(request, 'quiz/add_user_to_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
                                                                'quiz': quiz})
    if request.method == 'POST':   
        username_to_add = request.POST['username_input']
        # Input Validation: User cannot add self
        # if username_to_add == request.user.username:
        #     return render(request, 'quiz/add_user_to_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
        #                                                         'quiz': quiz, 'isError': True, 'error': 'You cannot add yourself.'})
        try:
            user = User.objects.get(username=username_to_add)
            userprofile = user.userprofile
        except Exception:
            return render(request, 'quiz/add_user_to_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
                                                                'quiz': quiz, 'isError': True, 'error': 'Username does not exist.'})
        else:
            quiz.users.add(userprofile)
            return render(request, 'quiz/add_user_to_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'dashboard',
                                                                'quiz': quiz, 'isSuccess': True, 'success': 'User added successfully.'})

@login_required
def take_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if UserProfile.objects.filter(quiz=quiz, user=request.user).count() < 1:
        return HttpResponseRedirect('/quiz/dashboard')
    if request.method == 'GET':
        # Retrieve questions for quiz
        questions = list(Question.objects.filter(quiz=quiz))
        questions_list = []
        # Retrieve answers for questions
        for question in questions:
            answers = []
            correct_answers_list = CorrectAnswer.objects.filter(question=question)
            incorrect_answers_list = IncorrectAnswer.objects.filter(question=question)
            for answer in correct_answers_list:
                answers.append(answer.text)
            for answer in incorrect_answers_list:
                answers.append(answer.text)
            if correct_answers_list.count() > 1:
                is_select_all = 1
            else:
                is_select_all = 0
            shuffle(answers)
            questions_list.append({'question': question.text, 'answers': answers, 'is_select_all': is_select_all})
        shuffle(questions_list)
        score = Score(user=request.user.userprofile, quiz=quiz, score=0, 
                        expiration_date=datetime.now(timezone.utc)+timedelta(minutes=quiz.time_limit,seconds=30))
        score.save()
        return render(request, 'quiz/take_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'take_quiz',
                                                        'questions': questions_list, 'time_limit': quiz.time_limit,
                                                        'quiz_id': quiz_id})
    if request.method == 'POST':
        score = Score.objects.filter(user=request.user.userprofile, quiz=quiz, score=0).order_by('-created_date')[0]
        if(quiz.time_limit != 0):
            if(score.expiration_date > datetime.now(timezone.utc)):
                return HttpResponseRedirect('/quiz/dashboard')
        print(request.POST)
        graded_list = []
        for number in range(Question.objects.filter(quiz=quiz).count()):
            question_answer = request.POST['answer_input'+str(number)].split('*QUESTION*')[1].split('*ANSWER*')
            question_text = question_answer[0]
            answers = question_answer[1:]
            # If question does not exist - evidence of tampering - mark question incorrect, do not create AnsweredQuestion entry
            try:
                question = Question.objects.get(quiz=quiz, text=question_text)
            except Exception:
                graded_list.append(False)
                continue
            # Get correct answers for question
            correct_answers_list = CorrectAnswer.objects.filter(question=question)
            # Check if multiple correct answers
            for answer in range(len(answers)):
                try:
                    CorrectAnswer.objects.get(question=question, text=answers[answer])
                except Exception:
                    graded_list.append(False)
                    # Create AnsweredQuestion entries for displaying detailed results.
                    answered_question = AnsweredQuestion(question=question, score=score, question_number=answer, is_correct=False)
                    answered_question.save()
                    for index in answers:
                        try:
                            correct_answer = CorrectAnswer.objects.get(question=question, text=index)
                        except Exception:
                            try:
                                incorrect_answer = IncorrectAnswer.objects.get(question=question, text=index)
                            except Exception:
                                # No answers selected
                                break
                            else:
                                answered_question.incorrect_answers_selected.add(incorrect_answer)
                                answered_question.save()
                        else:
                            answered_question.correct_answers_selected.add(correct_answer)
                            answered_question.save()
                    continue
                else:
                    if answer+1 == len(answers):
                        # Check if ALL correct answers were selected
                        if len(answers) < CorrectAnswer.objects.filter(question=question).count():
                            is_correct = False
                        else:
                            is_correct = True
                        # Create AnsweredQuestion entry
                        graded_list.append(is_correct)
                        answered_question = AnsweredQuestion(question=question, score=score, question_number=answer, is_correct=is_correct)
                        answered_question.save()
                        for selected_answer in answers:
                            correct_answer = CorrectAnswer.objects.get(question=question, text=selected_answer)
                            answered_question.correct_answers_selected.add(correct_answer)
                            answered_question.save()
        # Calculate Grade
        correct_count = 0
        for entry in graded_list:
            if entry == True:
                correct_count += 1
        grade = correct_count / len(graded_list) * 100
        score.score = round(grade, 1)
        score.save()
        return HttpResponseRedirect('/quiz/dashboard')

@login_required
def begin_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    if UserProfile.objects.filter(quiz=quiz, user=request.user).count() < 1:
        return HttpResponseRedirect('/quiz/dashboard')
    return render(request, 'quiz/begin_quiz.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'take_quiz',
                                                    'time_limit': quiz.time_limit, 'quiz': quiz})

@login_required
def view_submissions(request, quiz_id, user_id):
    try:
        quiz = Quiz.objects.get(name=quiz_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    try:
        userprofile = UserProfile.objects.get(id=user_id)
    except Exception:
        return HttpResponseRedirect('/quiz/dashboard')
    is_user_list_information = False
    if request.user.userprofile != userprofile:
        is_user_list_information = True
        try:
            quiz = Quiz.objects.get(name=quiz_id, quiz_owner=request.user.userprofile)
        except Exception:
            return HttpResponseRedirect('/quiz/dashboard')
    if request.method == 'GET':
        score_list = Score.objects.filter(quiz=quiz, user=userprofile).order_by('-created_date')
        print(score_list.count())
        return render(request, 'quiz/view_submissions.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'view_submissions',
                                                                'score_list': score_list, 'quiz_id': quiz_id, 'user_id': userprofile.id,
                                                                'score_list_len': score_list.count(), 
                                                                'is_user_list_information': is_user_list_information})
    if request.method == 'POST':
        score_id = request.POST['score_id']
        try:
            score = Score.objects.get(id=score_id)
        except Exception:
            return HttpResponseRedirect('/quiz/view_submissions/'+quiz_id+'/'+user_name)
        answered_questions_list = AnsweredQuestion.objects.filter(score=score).order_by('question_number')
        detailed_questions_list = []
        for answered_question in answered_questions_list:
            answers = []
            selected_answers = []
            correct_answers_list = CorrectAnswer.objects.filter(question=answered_question.question)
            incorrect_answers_list = IncorrectAnswer.objects.filter(question=answered_question.question)
            selected_correct_list = answered_question.correct_answers_selected.all()
            selected_incorrect_list = answered_question.incorrect_answers_selected.all()
            for answer in correct_answers_list:
                answers.append({'answer': answer.text, 'correct': 1})
            if correct_answers_list.count() > 1:
                is_select_all = 1
            else:
                is_select_all = 0
            for answer in incorrect_answers_list:
                answers.append({'answer': answer.text, 'correct': 0})
            for answer in selected_correct_list:
                selected_answers.append({'answer': answer.text, 'correct': 1})
            for answer in selected_incorrect_list:
                selected_answers.append({'answer': answer.text, 'correct': 0})
            if answered_question.is_correct == True:
                is_correct = 1
            else:
                is_correct = 0
            detailed_questions_list.append({'question': answered_question.question.text, 'answers': answers, 'is_correct': is_correct,
                                            'selected_answers': selected_answers, 'is_select_all': is_select_all})
        return render(request, 'quiz/view_submission.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'view_submission',
                                                                'detailed_questions_list': detailed_questions_list, 'quiz_id': quiz_id})