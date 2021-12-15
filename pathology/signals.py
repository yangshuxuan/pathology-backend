from datetime import datetime, timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import notify_user
from . import models

@receiver(post_save,sender=models.PathologyPictureItem)
def cut_image_for_new_image(sender,**kargs):
    if kargs['created']:
        notify_user(kargs['instance'].id)
        