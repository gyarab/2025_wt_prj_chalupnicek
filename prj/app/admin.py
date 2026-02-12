from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from app.models import Movie

class MovieResource(resources.ModelResource):
    class Meta:
        model = Movie

@admin.register(Movie)
class MovieAdmin(ImportExportModelAdmin):
    list_display = ('title', 'release_year')
    list_filter = ('release_year',)
    search_fields = ('title',)

    resource_class = MovieResource



        