from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        while True:
            i+=1
            print(f"iterate {i}")
            time.sleep(1.0)
