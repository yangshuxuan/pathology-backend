from datetime import datetime, timezone
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from .tasks import notify_user,notify_croper
from . import models

@receiver(post_save,sender=models.PathologyPictureItem)
def cut_image_for_new_image(sender,**kargs):
    if kargs['created']:
        notify_user(kargs['instance'].id)

@receiver(post_save,sender=models.Diagnosis)
def create_report_for_new_diagnosis(sender,**kargs):
    if kargs['created']:
        models.Report.objects.create(diagnosis=kargs['instance'])


@receiver(post_save,sender=models.PathologyPictureItem)
def create_diagnosis_for_ai(sender,**kargs):
    if kargs['created']:
        pic=kargs['instance']
        with transaction.atomic():
            ai = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(username="ai").first()
            diagnosis = models.Diagnosis.objects.create(patient=pic.patient)
            diagnosis.doctors.set([ai])
            diagnosis.save()
            models.DiagnosisItem.objects.create(diagnosis=diagnosis,pathologyPicture=pic)
        notify_user(pic.id)

@receiver(post_save,sender=models.LabelItem)
def crop_region_for_new_label(sender,**kargs):
    if kargs['created']:
        notify_croper(str(kargs['instance'].id))
        
