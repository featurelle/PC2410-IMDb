from django.apps import AppConfig


class ImdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imdb'

    def ready(self):
        from . import signals
        from . import tasks
