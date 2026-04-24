from ninja import NinjaAPI, ModelSchema, Schema
from typing import List
from .models import Movie

api = NinjaAPI()

class MovieSchema(ModelSchema):
    class Meta:
        model = Movie
        model_fields = "__all__"
        exclude = ["director"]
    director: str | None

class MovieListingSchema(Schema):
    count: int
    results: List[MovieSchema]

class MessageSchema(Schema):
    message: str

@api.get("/movie", response=MovieListingSchema)
def get_movies(request):
    movies = Movie.objects.all()
    out = []
    for movie in movies:
        out.append({
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "rating": movie.rating,
            "director": movie.director.name if movie.director else None
        })
    return {
        "count": len(out),
        "results": out
    }

@api.get("/movie/{movie_id}", response={200: MovieSchema, 404: MessageSchema})
def get_movie(request, movie_id: int):
    try:
        movie = Movie.objects.get(id=movie_id)
        return {
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "rating": movie.rating,
            "director": movie.director.name if movie.director else None
        }
    except Movie.DoesNotExist:
        return 404, {"message": "Movie not found"}