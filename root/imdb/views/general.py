from typing import Iterable
from django.db.models import Model
from django.views import generic

from .. import models, search, randoms

from .util.cache import get_cached_uptodate


class Index(generic.TemplateView):
    template_name = 'imdb/index.html'
    movies_limit = 5
    directors_limit = 5
    watchlist_limit = 5

    def get_cached_movies(self) -> Iterable[Model]:
        return get_cached_uptodate(
            cache_key='movies',
            model_manager=models.Movie.objects,
            query_func=randoms.randoms,
            source=models.Movie.objects.prefetch_related('ratings').all(),
            limit=self.movies_limit
        )

    def get_cached_directors(self) -> Iterable[Model]:
        return get_cached_uptodate(
            cache_key='directors',
            model_manager=models.Director.objects,
            query_func=randoms.randoms,
            source=models.Director.objects.all(),
            limit=self.directors_limit
        )

    def get_cached_watchlist(self) -> Iterable[Model]:
        user = self.request.user
        if user.is_authenticated:
            return get_cached_uptodate(
                cache_key=f'user-{user.id}:watchlist',
                model_manager=user.watchlist,
                query_func=randoms.randoms,
                source=user.watchlist.movies(),
                limit=self.watchlist_limit
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = self.get_cached_movies()
        context['directors'] = self.get_cached_directors()
        context['watchlist'] = self.get_cached_watchlist()
        return context


class Search(generic.TemplateView):
    template_name = 'imdb/search.html'

    def dispatch_search(self):
        return search.dispatch(
            self.request.GET.get('query'),
            self.request.GET.get('opt')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_results'] = self.dispatch_search()
        return context
