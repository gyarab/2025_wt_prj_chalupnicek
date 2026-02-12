from django.shortcuts import render

from app.models import Movie

def homepage(request):
    context = {
        'movies': Movie.objects.all(),
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')