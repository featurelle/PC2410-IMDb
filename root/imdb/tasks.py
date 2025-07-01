import os

from PIL import Image
from django.conf import settings
from django.db.models import Model
from django_rq import job

from . import models


def cleanup_media(media_root, model: Model, field):
    media_dir = os.path.join(media_root, 'mediafiles')
    used_files = set()
    for obj in model.objects.all():
        file_field = getattr(obj, field)
        if file_field:
            used_files.add(os.path.abspath(file_field.path))

    for media_file in os.listdir(media_dir):
        file_path = os.path.join(media_dir, media_file)
        if os.path.abspath(file_path) not in used_files:
            try:
                with open(file_path, 'rb') as f:
                    img = Image.open(f)
                    img.verify()
            except (IOError, SyntaxError):
                # Not an image file, ignore it
                continue
            os.remove(file_path)


@job
def cleanup_media_job():
    media_root = settings.MEDIA_ROOT
    models_ = [models.Director, models.Movie, models.UserProfile]
    field = 'pic'

    for model in models_:
        cleanup_media(media_root, model, field)
