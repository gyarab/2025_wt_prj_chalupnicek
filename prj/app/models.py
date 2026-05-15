from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Žánr"
        verbose_name_plural = "Žánry"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=255)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=64, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    photo_url = models.URLField(blank=True, default="")

    class Meta:
        verbose_name = "Režisér"
        verbose_name_plural = "Režiséři"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=255)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=64, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    photo_url = models.URLField(blank=True, default="")

    class Meta:
        verbose_name = "Herec / Herečka"
        verbose_name_plural = "Herci a herečky"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True, default="")
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    country = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")
    poster_url = models.URLField(blank=True, default="")
    director = models.ForeignKey(Director, null=True, blank=True, on_delete=models.SET_NULL, related_name="movies")
    actors = models.ManyToManyField(Actor, blank=True, related_name="movies")
    genres = models.ManyToManyField(Genre, blank=True, related_name="movies")

    class Meta:
        verbose_name = "Film"
        verbose_name_plural = "Filmy"
        ordering = ["-year", "title"]

    def __str__(self):
        if self.year:
            return f"{self.title} ({self.year})"
        return self.title

    @property
    def average_rating(self):
        agg = self.ratings.aggregate(avg=models.Avg("value"))
        return agg["avg"]


class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Komentář"
        verbose_name_plural = "Komentáře"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}"


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField(help_text="Hodnocení 1–10")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hodnocení"
        verbose_name_plural = "Hodnocení"
        ordering = ["-created_at"]
        unique_together = [("movie", "user")]

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}: {self.value}"
