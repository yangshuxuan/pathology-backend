from background_task import background
from .models import PathologyPictureItem
from pathlib import PurePath
from django.conf import settings
import subprocess
import os
from pathlib import Path
import hashlib
from qingstor.sdk.service.qingstor import QingStor
from qingstor.sdk.config import Config

config = Config('1', '2')
qingstor = QingStor(config)
bucket_name='wuyuan'
bucket = qingstor.Bucket('wuyuan', 'sh1a')
def readImage(object_key):
    part_size = 1024 * 1024 * 5  # 5M every part.
    # ensure the file we will write to does not exists.
    if os.path.exists(object_key):
        os.remove(object_key)
    i = 0
    while True:
        lo = part_size * i
        hi = part_size * (i + 1) - 1
        byte_range = "bytes=%d-%d" % (lo, hi)
        output = bucket.get_object(object_key=object_key, range=byte_range)
        if output.status_code != 206:
            print("Get object(name: {}) by segment in bucket({}) failed with given message: {}".format(
                object_key,
                bucket_name,
                str(output.content, 'utf-8')))
            os.remove("/tmp/" + object_key)
            break
        else:
            with open("/tmp/" + object_key, 'a+b') as f:  # append to file in binary mode
                f.write(output.content)
            if len(output.content) < part_size:
                break
            i += 1
def writeImage(p):
    object_key = str(p)
    content_md5 = calculate_md5(object_key)
    
    with p.open(mode="rb") as f:
        output = bucket.put_object(object_key=object_key, content_type="image/jpeg",content_md5=content_md5,x_qs_storage_class="STANDARD", body=f)
    if output.status_code != 201:
        print("Upload object(name: {}) to bucket({}) failed with given message: {}".format(object_key,"wuyuan",str(output.content, 'utf-8')))
    else:
        print("Upload success")
    print(object_key)

def calculate_md5(filepath) -> str:
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

@background(schedule=1)
def notify_user(pathologyPictureItem_id):
    pathologyPictureItem = PathologyPictureItem.objects.get(pk=pathologyPictureItem_id)
    fileName = pathologyPictureItem.pathologyPicture.name
    readImage(fileName)
    littleImageAfterCut = str(PurePath(fileName).stem)
    subprocess.run([settings.CUT_TOOL, "dzsave",fileName,littleImageAfterCut])
    for dirpath, dirnames, files in os.walk(littleImageAfterCut):
        for file_name in files:
            p=Path(dirpath,file_name)
            writeImage(p)
    writeImage(Path(f"{littleImageAfterCut}.dzi"))
            

    pathologyPictureItem.isCutted=True
    pathologyPictureItem.save()
