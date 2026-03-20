from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    director = models.ForeignKey('Director', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.title} ({self.year})"

class Director(models.Model):
    name = models.CharField(max_length=255)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)

class Genre(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ManyToManyField('Movie')