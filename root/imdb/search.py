from django.db import models as m
from django.db.models import functions as f

from . import models


# Here come search functions registered with @register_type('search_key')
_search_dispatcher = {}


def register_type(search_key: str):
    def search_registry(func):
        _search_dispatcher[search_key] = func
        return func
    return search_registry


@register_type('movies')
def search_movies(query: str) -> dict:
    return {
        'movies': models.Movie.objects.annotate(
            titleyear=f.Concat('title', m.Value(' '), 'year', output_field=m.CharField())
        ).filter(titleyear__icontains=query) or None
    }


@register_type('directors')
def search_directors(query: str) -> dict:
    return {
        'directors': models.Director.objects.annotate(
            firstlast=f.Concat('first', m.Value(' '), 'last', output_field=m.CharField()),
        ).filter(firstlast__icontains=query) or None
    }


@register_type('all')
def search_all(query: str) -> dict:
    return {
        'directors': search_directors(query)['directors'],
        'movies': search_movies(query)['movies']
    }


def dispatch(query: str, search_type: str) -> dict:
    """Chooses the search function based on *search_type* and returns the search results and parameters"""

    if search_type not in _search_dispatcher:
        raise KeyError(f'''There's no such search type registered: "{search_type}"''')

    # returns also empty keys or found results in all or some keys
    results = {
            'query': query,
            'search_type': search_type,
    } | {
        key: None for key in _search_dispatcher.keys()
    }

    if query:
        results |= _search_dispatcher[search_type](query)

    return results
