import random

from django.db import models


def randoms(source: models.QuerySet, limit: int) -> list[models.Model]:
    source_len = len(source)
    if limit > source_len:
        limit = source_len
    return random.sample(list(source), k=limit)
