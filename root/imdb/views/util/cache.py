from typing import Iterable

from django.core.cache import cache
from django.db.models import Model
from django.utils import timezone


def get_cached_uptodate(cache_key: str, model_manager,
                        query_func, **kwargs) -> Iterable[Model]:
    """Sets new cache if data wasn't cached before or if it's not up-to-date, otherwise just returns cached data"""
    cached_data = cache.get(cache_key)
    if not cached_data:
        cached_data = query_func(**kwargs)
        cache.set(cache_key, cached_data, 60)
    else:
        latest_updated_at = model_manager.latest('timestamp').timestamp
        cached_updated_at = cache.get(f'{cache_key}:updated')
        if cached_updated_at is None or cached_updated_at < latest_updated_at:
            cached_data = query_func(**kwargs)
            cache.set(cache_key, cached_data, 60)
        cache.set(f'{cache_key}:updated', timezone.now(), 60)

    return cached_data
