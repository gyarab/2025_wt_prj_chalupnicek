from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from app import views
from app.api import api


urlpatterns = [
    path("api/", api.urls),
    path("admin/", admin.site.urls),
    # `/` je rozcestník mezi Django frontendem a Vue SPA frontendem (port 5173).
    path("", views.render_landing, name="landing"),
    # Původní Django movie list je teď na /movies/. Pojmenování `home` zachováváme,
    # aby `LOGIN_REDIRECT_URL = 'home'` a všechny `{% url 'home' %}` v šablonách dál fungovaly.
    path("movies/", views.render_movies, name="home"),
    path("about/", views.render_about, name="about"),
    path("api_playground/", views.render_api_playground, name="api_playground"),
    path("movie/<int:movie_id>/", views.render_movie_detail, name="movie_detail"),
    path("movie/<int:movie_id>/comment/", views.post_comment, name="comment_movie"),
    path("movie/<int:movie_id>/rate/", views.post_rating, name="rate_movie"),
    path("directors/", views.render_directors, name="directors"),
    path("directors/<int:director_id>/", views.render_director_detail, name="director_detail"),
    path("actors/", views.render_actors, name="actors"),
    path("actors/<int:actor_id>/", views.render_actor_detail, name="actor_detail"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("accounts/register/", views.register, name="register"),
]
