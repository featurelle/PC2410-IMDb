from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from . import models


class PicDisplayMixin:

    @admin.display(description='Pic display')
    def pic_display(self, obj):
        return mark_safe(f'<img src="{obj.pic.url}" width="150" height="auto">')


@admin.register(models.Director)
class DirectorAdmin(admin.ModelAdmin, PicDisplayMixin):

    class MoviesInline(admin.TabularInline):
        model = models.Director.movies.through
        verbose_name = 'movie'

    list_display = ('last', 'first', 'slug', 'rating')
    inlines = [
        MoviesInline
    ]
    list_display_links = list_display
    prepopulated_fields = {'slug': ('first', 'last')}
    readonly_fields = ('pic_display',)


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin, PicDisplayMixin):

    class DirectorsInline(admin.TabularInline):
        model = models.Movie.directors.through
        verbose_name = 'director'

    list_display = ('title', 'year', 'directors_list')
    inlines = [
        DirectorsInline
    ]
    prepopulated_fields = {'slug': ('title', 'year')}
    exclude = ('directors', 'views')
    readonly_fields = ('pic_display',)

    @admin.display(description='Directors')
    def directors_list(self, movie) -> list[str]:
        return list(map(str, movie.directors.all()))


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin, PicDisplayMixin):
    readonly_fields = ('pic_display',)


class UserAdmin(DefaultUserAdmin):

    class UserProfileInline(admin.TabularInline, PicDisplayMixin):
        model = models.UserProfile
        verbose_name = 'profile'
        readonly_fields = ('pic_display',)

    inlines = admin.site._registry.get(User).inlines + (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(models.MovieComment)
class MovieCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MovieRatingScore)
class MovieRatingScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WatchlistEntry)
class WatchlistEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MovieView)
class MovieViewAdmin(admin.ModelAdmin):
    pass
