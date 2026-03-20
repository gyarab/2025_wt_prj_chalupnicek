from django.contrib import admin
from .models import Movie, Director, Genre

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'year']
    search_fields = ['title']


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_year']
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
