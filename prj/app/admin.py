from django.contrib import admin
from django.utils.html import format_html

from .models import Movie, Director, Actor, Genre, Comment, Rating


admin.site.site_header = "FilmDB administrace"
admin.site.site_title = "FilmDB administrace"
admin.site.index_title = "Vítejte v administraci"


def _thumb(url, size=40):
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:4px;" />',
        url, size, size,
    )


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ["user", "text", "created_at"]
    can_delete = True


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ["user", "value", "created_at"]
    can_delete = True


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["poster_thumb", "title", "year", "director", "country", "duration_minutes", "avg_rating"]
    list_display_links = ["poster_thumb", "title"]
    list_filter = ["year", "country", "genres", "director"]
    search_fields = ["title", "original_title", "description", "director__name", "actors__name"]
    autocomplete_fields = ["director", "actors", "genres"]
    inlines = [CommentInline, RatingInline]
    fieldsets = (
        ("Základní údaje", {
            "fields": ("title", "original_title", "year", "country", "duration_minutes", "poster_url"),
        }),
        ("Obsah", {
            "fields": ("description",),
        }),
        ("Vazby", {
            "fields": ("director", "actors", "genres"),
        }),
    )

    @admin.display(description="Plakát")
    def poster_thumb(self, obj):
        return _thumb(obj.poster_url, 50)

    @admin.display(description="Průměr")
    def avg_rating(self, obj):
        avg = obj.average_rating
        if avg is None:
            return "—"
        return f"{avg:.1f}"


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ["photo_thumb", "name", "birth_year", "nationality", "movie_count"]
    list_display_links = ["photo_thumb", "name"]
    list_filter = ["nationality"]
    search_fields = ["name", "bio"]

    @admin.display(description="Foto")
    def photo_thumb(self, obj):
        return _thumb(obj.photo_url)

    @admin.display(description="Filmů")
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ["photo_thumb", "name", "birth_year", "nationality", "movie_count"]
    list_display_links = ["photo_thumb", "name"]
    list_filter = ["nationality"]
    search_fields = ["name", "bio"]

    @admin.display(description="Foto")
    def photo_thumb(self, obj):
        return _thumb(obj.photo_url)

    @admin.display(description="Filmů")
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "movie_count"]
    search_fields = ["name"]

    @admin.display(description="Filmů")
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["short_text", "user", "movie", "created_at"]
    list_filter = ["created_at", "movie"]
    search_fields = ["text", "user__username", "movie__title"]
    autocomplete_fields = ["movie", "user"]
    readonly_fields = ["created_at"]

    @admin.display(description="Text")
    def short_text(self, obj):
        return (obj.text[:60] + "…") if len(obj.text) > 60 else obj.text


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "value", "created_at"]
    list_filter = ["value", "created_at"]
    search_fields = ["user__username", "movie__title"]
    autocomplete_fields = ["movie", "user"]
    readonly_fields = ["created_at"]


# Vlastní úvodní stránka administrace je řešena pouze přepsáním šablony
# v souboru templates/admin/index.html. Funguje to díky tomu, že aplikace 'app'
# je v INSTALLED_APPS uvedena před 'django.contrib.admin' – Django při hledání
# šablony narazí na naši verzi dříve než na výchozí. Žádný vlastní view tedy
# nepotřebujeme.
