from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'is_logged_in': request.user.is_authenticated, 'isActive': 'home', 'user': request.user.username})