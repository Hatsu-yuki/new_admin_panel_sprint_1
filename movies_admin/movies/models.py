import uuid
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('genre'), max_length=255)
    description = models.TextField(_('genre_description'), blank=True)


    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [models.UniqueConstraint(fields=['film_work_id', 'genre_id'],
                                               name='genre_film_work_idx')]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [models.UniqueConstraint(fields=['film_work_id', 'person_id', 'role'],
                                               name='person_film_work_idx')]





class FilmWork(UUIDMixin, TimeStampedMixin):
    class FilmWorkType(models.TextChoices):
        MOVIE = "MV", _('movie')
        TV_SHOW = "TV", _("tvshow")

    title = models.CharField(_('title'), max_length=255)
    description = models.CharField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'))
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')
    rating = models.FloatField(_('rating'),
                                blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)]
                               )
    type = models.CharField(_('type'),
                        max_length=2,
                        choices=FilmWorkType.choices,
                        default=FilmWorkType.MOVIE,
                            )
    certificate = models.CharField(_('certificate'), max_length=512, blank=True)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')


    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film_work')
        verbose_name_plural = _('film_works')

    def __str__(self):
        return self.title




