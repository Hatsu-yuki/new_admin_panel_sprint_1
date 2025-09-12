from django.contrib import admin
from .models import Genre, FilmWork, Person, GenreFilmWork, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('full_name',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline,
               PersonFilmWorkInline,)
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type', 'creation_date', 'rating')
    search_fields = ('title', 'description', 'id')


