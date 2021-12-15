from background_task import background
from .models import PathologyPictureItem
from pathlib import PurePath
from django.conf import settings
import subprocess

@background(schedule=1)
def notify_user(pathologyPictureItem_id):
    pathologyPictureItem = PathologyPictureItem.objects.get(pk=pathologyPictureItem_id)
    f = PurePath(pathologyPictureItem.pathologyPicture.path)
    v = f.parent / f.stem
    subprocess.run([settings.CUT_TOOL, "dzsave",str(f),str(v)])
    pathologyPictureItem.isCutted=True
    pathologyPictureItem.save()