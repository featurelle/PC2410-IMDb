from django.contrib.auth.models import User
from django.db import models
from django.core import validators
from django.db.models import QuerySet
from django.utils import timezone

from . import randoms


class Director(models.Model):

    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    pic = models.ImageField(null=True, blank=True, upload_to='imdb/directors/')
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    # movies

    @property
    def fullname(self) -> str:
        return f'{self.first} {self.last}'

    @property
    def rating(self) -> float | None:
        return self.movies.annotate(movie_rating=models.Avg('ratings__score'))\
            .aggregate(rating_avg=models.Avg('movie_rating'))['rating_avg'] or None

    @property
    def best_trailer(self) -> str | None:
        if best := self.movies.annotate(rating_avg=models.Avg('ratings__score')).order_by('-rating_avg'):
            return best[0].trailer or None

    @property
    def random_trailer(self) -> str | None:
        if movies := self.movies.filter(trailer__isnull=False):
            return randoms.randoms(movies, limit=1)[0].trailer

    @property
    def creative_period(self) -> dict[str, int]:
        years = self.movies.aggregate(start=models.Min('year'), end=models.Max('year'))
        return {
            'start': years['start'] or None,
            'end': years['end'] or None
        }

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.fullname}>'

    def __str__(self):
        return f'{self.fullname}'


class Movie(models.Model):

    directors = models.ManyToManyField(Director, blank=True, related_name='movies')
    title = models.CharField(max_length=128)
    plot = models.TextField(null=True, blank=True)
    pic = models.ImageField(null=True, blank=True, upload_to='imdb/movies/')
    trailer = models.URLField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(1888),
            validators.MaxValueValidator(timezone.now().year + 20)
        ]
    )
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    # views
    # watchlist
    # comments
    # ratings

    @property
    def rating(self) -> float | None:
        return self.ratings.aggregate(score_avg=models.Avg('score'))['score_avg'] or None

    @property
    def watchers(self) -> QuerySet[User]:
        return User.objects.filter(watchlist__movie=self)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.title} ({self.year})>'

    def __str__(self):
        return f'{self.title} ({self.year})'


class MovieView(models.Model):
    class MovieViewEntryManager(models.Manager):
        def movies(self):
            return Movie.objects.filter(views__in=self.all())

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='views')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='views')
    session_key = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = MovieViewEntryManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'user'],
                name='movie_user_unique_view',
                violation_error_message='Movie view should be unique for each user and movie',
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['movie', 'session_key'],
                name='movie_anon_session_unique_view',
                violation_error_message='Movie view should be unique for each anon session and movie',
                condition=models.Q(user__isnull=True)
            )
        ]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.session_key} by {self.user.username if self.user else "Anon"}' \
               f', viewed "{self.movie.title}({self.movie.year})">'

    def __str__(self):
        return f'{self.user.username if self.user else "Anon"} viewed "{self.movie.title}({self.movie.year})"'


class WatchlistEntry(models.Model):
    class WatchlistEntryManager(models.Manager):
        def movies(self):
            return Movie.objects.filter(watchlist__in=self.all())

    user = models.ForeignKey(User, related_name='watchlist', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='watchlist', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = WatchlistEntryManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='user_movie_unique_watchlist_entry',
                violation_error_message='User cannot have multiple watchlist entries on the same movie.'
            ),
        ]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.user.username} watching "{self.movie.title}" ({self.movie.year})>'

    def __str__(self):
        return f'{self.user.username} watching "{self.movie.title}" ({self.movie.year})'


class MovieComment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField(max_length=512)
    timestamp = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.user.username}' \
               f' comment on "{self.movie.title}" ({self.movie.year}) [{self.timestamp}]>'

    def __str__(self):
        return f'{self.user.username} comment on "{self.movie.title}" ({self.movie.year}) [{self.timestamp}]'


class MovieRatingScore(models.Model):
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(10)
        ]
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(score__gte=1, score__lte=10),
                name='movieratingscore_1upto10',
                violation_error_message='A movie rating score must be from 1 up to 10'
            ),
            models.UniqueConstraint(
                fields=['movie', 'user'],
                name='users_movie_rating_unique',
                violation_error_message='User cannot have multiple ratings on the same movie.'
                                        ' Change the existing rating score instead'
            )
        ]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.user.username} => {self.score} stars to' \
               f' "{self.movie.title}" ({self.movie.year})>'

    def __str__(self):
        return f'{self.user.username} gave {self.score} stars to "{self.movie.title}" ({self.movie.year})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    pic = models.ImageField(null=True, blank=True, upload_to='imdb/users/')

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.user.username}">'

    def __str__(self):
        return f'{self.user.username}'


class MockModel(models.Model):
    pass
