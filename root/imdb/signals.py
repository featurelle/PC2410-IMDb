from django.db.models.signals import post_delete
from django.dispatch import receiver

from . import models


@receiver(post_delete, sender=models.UserProfile)
@receiver(post_delete, sender=models.Director)
@receiver(post_delete, sender=models.Movie)
def clear_media(sender, instance, *args, **kwargs):
    if instance.pic:
        instance.pic.delete()
        instance.delete()
