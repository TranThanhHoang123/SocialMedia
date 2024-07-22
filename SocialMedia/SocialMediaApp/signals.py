from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import *

@receiver(post_delete, sender=Media)
def delete_media_file(sender, instance, **kwargs):
    instance.file.delete(False)

@receiver(post_delete, sender=Comment)
def delete_comment_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(False)