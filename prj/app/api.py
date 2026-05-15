from typing import List, Optional

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from .models import Actor, Comment, Director, Genre, Movie, Rating

api = NinjaAPI(title="FilmDB API", description="REST API filmové databáze FilmDB.")


# ---------- Schemas ----------

class MessageSchema(Schema):
    message: str


class GenreOut(Schema):
    id: int
    name: str


class PersonOut(Schema):
    id: int
    name: str
    birth_year: Optional[int] = None
    nationality: str = ""
    photo_url: str = ""


class MovieOut(Schema):
    id: int
    title: str
    original_title: str = ""
    year: Optional[int] = None
    duration_minutes: Optional[int] = None
    country: str = ""
    description: str = ""
    poster_url: str = ""
    director: Optional[PersonOut] = None
    actors: List[PersonOut] = []
    genres: List[GenreOut] = []
    average_rating: Optional[float] = None


class MovieListItem(Schema):
    id: int
    title: str
    year: Optional[int] = None
    poster_url: str = ""
    director: Optional[str] = None
    average_rating: Optional[float] = None


class MovieListingSchema(Schema):
    count: int
    results: List[MovieListItem]


class MovieIn(Schema):
    title: str
    original_title: str = ""
    year: Optional[int] = None
    duration_minutes: Optional[int] = None
    country: str = ""
    description: str = ""
    poster_url: str = ""
    director_id: Optional[int] = None
    actor_ids: List[int] = []
    genre_ids: List[int] = []


class CommentOut(Schema):
    id: int
    movie_id: int
    user: str
    text: str
    created_at: str


class CommentIn(Schema):
    text: str


class RatingOut(Schema):
    id: int
    movie_id: int
    user: str
    value: int


class RatingIn(Schema):
    value: int


# ---------- Helpers ----------

def _movie_to_out(movie: Movie) -> dict:
    avg = movie.ratings.aggregate(avg=Avg("value"))["avg"]
    return {
        "id": movie.id,
        "title": movie.title,
        "original_title": movie.original_title,
        "year": movie.year,
        "duration_minutes": movie.duration_minutes,
        "country": movie.country,
        "description": movie.description,
        "poster_url": movie.poster_url,
        "director": (
            {
                "id": movie.director.id,
                "name": movie.director.name,
                "birth_year": movie.director.birth_year,
                "nationality": movie.director.nationality,
                "photo_url": movie.director.photo_url,
            }
            if movie.director
            else None
        ),
        "actors": [
            {
                "id": a.id,
                "name": a.name,
                "birth_year": a.birth_year,
                "nationality": a.nationality,
                "photo_url": a.photo_url,
            }
            for a in movie.actors.all()
        ],
        "genres": [{"id": g.id, "name": g.name} for g in movie.genres.all()],
        "average_rating": round(avg, 2) if avg is not None else None,
    }


def _apply_movie_input(movie: Movie, payload: MovieIn) -> Movie:
    movie.title = payload.title
    movie.original_title = payload.original_title
    movie.year = payload.year
    movie.duration_minutes = payload.duration_minutes
    movie.country = payload.country
    movie.description = payload.description
    movie.poster_url = payload.poster_url
    if payload.director_id is not None:
        movie.director = get_object_or_404(Director, pk=payload.director_id)
    else:
        movie.director = None
    movie.save()
    movie.actors.set(Actor.objects.filter(id__in=payload.actor_ids))
    movie.genres.set(Genre.objects.filter(id__in=payload.genre_ids))
    return movie


# ---------- Movie endpoints ----------

@api.get("/movie", response=MovieListingSchema, tags=["movies"])
def list_movies(request, q: str = "", year: Optional[int] = None,
                genre_id: Optional[int] = None, director_id: Optional[int] = None,
                actor_id: Optional[int] = None):
    movies = Movie.objects.all().annotate(avg=Avg("ratings__value")).select_related("director")
    if q:
        movies = movies.filter(title__icontains=q)
    if year is not None:
        movies = movies.filter(year=year)
    if genre_id is not None:
        movies = movies.filter(genres__id=genre_id)
    if director_id is not None:
        movies = movies.filter(director__id=director_id)
    if actor_id is not None:
        movies = movies.filter(actors__id=actor_id)
    movies = movies.distinct()

    results = [
        {
            "id": m.id,
            "title": m.title,
            "year": m.year,
            "poster_url": m.poster_url,
            "director": m.director.name if m.director else None,
            "average_rating": round(m.avg, 2) if m.avg is not None else None,
        }
        for m in movies
    ]
    return {"count": len(results), "results": results}


@api.get("/movie/{movie_id}", response={200: MovieOut, 404: MessageSchema}, tags=["movies"])
def get_movie(request, movie_id: int):
    try:
        movie = Movie.objects.prefetch_related("actors", "genres").select_related("director").get(pk=movie_id)
    except Movie.DoesNotExist:
        return 404, {"message": "Film nebyl nalezen."}
    return _movie_to_out(movie)


@api.post("/movie", response={201: MovieOut}, auth=django_auth, tags=["movies"])
def create_movie(request, payload: MovieIn):
    movie = _apply_movie_input(Movie(), payload)
    return 201, _movie_to_out(movie)


@api.put("/movie/{movie_id}", response={200: MovieOut, 404: MessageSchema}, auth=django_auth, tags=["movies"])
def update_movie(request, movie_id: int, payload: MovieIn):
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        return 404, {"message": "Film nebyl nalezen."}
    movie = _apply_movie_input(movie, payload)
    return _movie_to_out(movie)


@api.delete("/movie/{movie_id}", response={204: None, 404: MessageSchema}, auth=django_auth, tags=["movies"])
def delete_movie(request, movie_id: int):
    try:
        Movie.objects.get(pk=movie_id).delete()
    except Movie.DoesNotExist:
        return 404, {"message": "Film nebyl nalezen."}
    return 204, None


# ---------- Comment endpoints ----------

@api.get("/movie/{movie_id}/comments", response=List[CommentOut], tags=["comments"])
def list_comments(request, movie_id: int):
    comments = Comment.objects.filter(movie_id=movie_id).select_related("user")
    return [
        {
            "id": c.id,
            "movie_id": c.movie_id,
            "user": c.user.username,
            "text": c.text,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]


@api.post("/movie/{movie_id}/comments", response={201: CommentOut, 404: MessageSchema},
          auth=django_auth, tags=["comments"])
def create_comment(request, movie_id: int, payload: CommentIn):
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        return 404, {"message": "Film nebyl nalezen."}
    c = Comment.objects.create(movie=movie, user=request.user, text=payload.text)
    return 201, {
        "id": c.id,
        "movie_id": c.movie_id,
        "user": c.user.username,
        "text": c.text,
        "created_at": c.created_at.isoformat(),
    }


# ---------- Rating endpoints ----------

@api.get("/movie/{movie_id}/ratings", response=List[RatingOut], tags=["ratings"])
def list_ratings(request, movie_id: int):
    ratings = Rating.objects.filter(movie_id=movie_id).select_related("user")
    return [
        {"id": r.id, "movie_id": r.movie_id, "user": r.user.username, "value": r.value}
        for r in ratings
    ]


@api.put("/movie/{movie_id}/rate", response={200: RatingOut, 404: MessageSchema},
         auth=django_auth, tags=["ratings"])
def rate_movie(request, movie_id: int, payload: RatingIn):
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        return 404, {"message": "Film nebyl nalezen."}
    rating, _ = Rating.objects.update_or_create(
        movie=movie, user=request.user, defaults={"value": payload.value}
    )
    return {"id": rating.id, "movie_id": rating.movie_id, "user": rating.user.username, "value": rating.value}
