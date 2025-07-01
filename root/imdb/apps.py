from django.apps import AppConfig


class ImdbConfig(AppConfig):
    name = 'imdb'

    def ready(self):
        from . import signals
