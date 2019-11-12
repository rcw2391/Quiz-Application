from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=20, min_length=8)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput, max_length=20)