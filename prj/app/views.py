from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, RatingForm, RegisterForm
from .models import Actor, Director, Genre, Movie, Rating


def render_landing(request):
    # `/` slouží jako rozcestník mezi dvěma frontendy:
    # - klasický Django HTML frontend (server-rendered) na /movies/
    # - Vue SPA frontend: v dev běží na http://localhost:5173/, v produkci ho
    #   nginx servíruje pod /app/. Odkaz dodává context processor (vue_frontend_url).
    return render(request, "landing.html")


def render_movies(request):
    movies = Movie.objects.all().annotate(avg=Avg("ratings__value")).select_related("director")

    q = request.GET.get("q", "").strip()
    selected_year = request.GET.get("year", "").strip()
    selected_genre = request.GET.get("genre", "").strip()
    selected_director = request.GET.get("director", "").strip()
    selected_actor = request.GET.get("actor", "").strip()

    if q:
        movies = movies.filter(Q(title__icontains=q) | Q(original_title__icontains=q))
    if selected_year.isdigit():
        movies = movies.filter(year=int(selected_year))
    if selected_genre.isdigit():
        movies = movies.filter(genres__id=int(selected_genre))
    if selected_director.isdigit():
        movies = movies.filter(director__id=int(selected_director))
    if selected_actor.isdigit():
        movies = movies.filter(actors__id=int(selected_actor))

    movies = movies.distinct()

    years = (
        Movie.objects.exclude(year__isnull=True)
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    context = {
        "movies": movies,
        "q": q,
        "years": years,
        "genres": Genre.objects.all(),
        "directors": Director.objects.all(),
        "actors": Actor.objects.all(),
        "selected_year": selected_year,
        "selected_genre": selected_genre,
        "selected_director": selected_director,
        "selected_actor": selected_actor,
    }
    return render(request, "home.html", context)


def render_about(request):
    return render(request, "about.html")


def render_api_playground(request):
    return render(request, "api_playground.html")


def render_movie_detail(request, movie_id):
    movie = get_object_or_404(
        Movie.objects.select_related("director").prefetch_related("actors", "genres"),
        pk=movie_id,
    )
    comments = movie.comments.select_related("user").all()
    avg_rating = movie.ratings.aggregate(avg=Avg("value"))["avg"]
    ratings_count = movie.ratings.count()

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(movie=movie, user=request.user).first()

    context = {
        "movie": movie,
        "comments": comments,
        "avg_rating": avg_rating,
        "ratings_count": ratings_count,
        "user_rating": user_rating,
        "comment_form": CommentForm(),
        "rating_form": RatingForm(instance=user_rating),
        "rating_values": range(1, 11),
    }
    return render(request, "movie_detail.html", context)


@login_required
def post_comment(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.user = request.user
            comment.save()
            messages.success(request, "Komentář byl přidán.")
        else:
            messages.error(request, "Komentář se nepodařilo přidat.")
    return HttpResponseRedirect(reverse("movie_detail", args=[movie.id]))


@login_required
def post_rating(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={"value": form.cleaned_data["value"]},
            )
            messages.success(request, "Hodnocení bylo uloženo.")
        else:
            messages.error(request, "Hodnocení se nepodařilo uložit.")
    return HttpResponseRedirect(reverse("movie_detail", args=[movie.id]))


def render_directors(request):
    q = request.GET.get("q", "").strip()
    directors = Director.objects.all()
    if q:
        directors = directors.filter(name__icontains=q)
    return render(request, "directors.html", {"directors": directors, "q": q})


def render_director_detail(request, director_id):
    director = get_object_or_404(Director, pk=director_id)
    movies = director.movies.all().annotate(avg=Avg("ratings__value")).order_by("-year")
    return render(request, "director_detail.html", {"director": director, "movies": movies})


def render_actors(request):
    q = request.GET.get("q", "").strip()
    actors = Actor.objects.all()
    if q:
        actors = actors.filter(name__icontains=q)
    return render(request, "actors.html", {"actors": actors, "q": q})


def render_actor_detail(request, actor_id):
    actor = get_object_or_404(Actor, pk=actor_id)
    movies = actor.movies.all().annotate(avg=Avg("ratings__value")).order_by("-year")
    return render(request, "actor_detail.html", {"actor": actor, "movies": movies})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Účet byl vytvořen, vítej!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})
