from uuid import uuid4
from django.db import models

# Create your models here.
class Patient(models.Model):
    name = models.CharField(max_length=255,verbose_name="病人姓名")
    sex = models.CharField(max_length=255,verbose_name="性别")
    age = models.PositiveSmallIntegerField(blank=True,null=True,verbose_name="年龄")

    class Meta:
        verbose_name = '病人'
        verbose_name_plural = '病人集'
class  PathologyPictureItem(models.Model):
    pathologyPicture = models.FileField(verbose_name="病理图片")
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="图片上传时间")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,verbose_name="患者")
    description = models.TextField(blank=True,null=True,verbose_name="图片描述")
    isCutted = models.BooleanField(default=False,verbose_name="是否已经切图")

    class Meta:
        verbose_name = '病理图片'
        verbose_name_plural = '病理图片集'


class LabelItem(models.Model):
    MUSHROOM = 'M'
    CATEGORY_CHOICES = [
        (MUSHROOM, '真菌')
    ]
    id = models.UUIDField(primary_key=True,default=uuid4)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="标注时间")
    modifiedAt = models.DateTimeField(auto_now=True,verbose_name="标注更新时间")
    pathologypictureitem = models.ForeignKey(PathologyPictureItem,on_delete=models.PROTECT,verbose_name="诊断")
    category = models.CharField(
        max_length=4, choices=CATEGORY_CHOICES, default=MUSHROOM,verbose_name="类别")
    x = models.FloatField(verbose_name="标注起点坐标X")
    y = models.FloatField(verbose_name="标注起点坐标Y")
    w = models.FloatField(verbose_name="标注宽度")
    h = models.FloatField(verbose_name="标注高度")
    zoomLevel = models.FloatField(verbose_name="标注时放大倍数")
    regionPicture = models.FileField(blank=True,null=True,verbose_name="标注区域图")
    def getPathologyPictureItemId(self):
        return self.pathologypictureitem.id
    class Meta:
        verbose_name = '标注'
        verbose_name_plural = '标注集'