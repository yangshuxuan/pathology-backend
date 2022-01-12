from django.conf import settings
from django.core.management.base import BaseCommand
# from authentication.models import Account
from django.apps import apps

class Command(BaseCommand):

    def handle(self, *args, **options):
        usermodel = apps.get_model(settings.AUTH_USER_MODEL)
        if usermodel.objects.count() == 0:
            for user in settings.ADMINS:
                username = user[0].replace(' ', '')
                email = user[1]
                password = 'admin'
                print('Creating account for %s (%s)' % (username, email))
                admin = usermodel.objects.create_superuser(email=email, username=username, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
        ai = usermodel.objects.filter(username="ai").first()
        if not ai:
            ai = usermodel.objects.create(email="ai@163.com", username="ai", password="ai")
            ai.is_active = True
            ai.save()
