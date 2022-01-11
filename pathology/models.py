from uuid import uuid4
from django.contrib import admin
from django.db import models
from django.conf import settings


class Patient(models.Model):
    name = models.CharField(max_length=255,verbose_name="病人姓名")
    sex = models.CharField(max_length=255,verbose_name="性别")
    age = models.PositiveSmallIntegerField(blank=True,null=True,verbose_name="年龄")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = '病人'
        verbose_name_plural = '病人集'

class  PathologyPictureItem(models.Model):
    pathologyPicture = models.FileField(verbose_name="病理图片",upload_to=settings.ORIGIN_IMAGES_LOCATION)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="图片上传时间")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,verbose_name="患者")
    description = models.TextField(verbose_name="图片描述")
    isCutted = models.BooleanField(default=False,verbose_name="是否已经切图")
    def __str__(self) -> str:
        return f"{self.patient} {self.createdAt} {self.description}"

    class Meta:
        verbose_name = '病理图片'
        verbose_name_plural = '病理图片集'





class  Diagnosis(models.Model):
    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="诊断创建时间")

    last_update = models.DateTimeField(auto_now=True,verbose_name="诊断更新时间")
    
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT,verbose_name="患者",related_name='diagnoses')
    
    doctors = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name="医生")
    
    description = models.TextField(blank=True,null=True,verbose_name="诊断描述")

    isFinished = models.BooleanField(default=False,verbose_name="诊断是否完成")

    def __str__(self) -> str:
        return f"{self.patient.name} ID为{self.id}的诊断"
    
    @admin.display(description="诊断医生")
    def doctorNames(self):
        return ",".join([ d.username for d in list(self.doctors.all())])
    class Meta:
        verbose_name = '诊断'
        verbose_name_plural = '诊断集'


class  DiagnosisItem(models.Model):
    """
    每个诊断至少有一张图片
    """

    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="诊断项创建时间")

    last_update = models.DateTimeField(auto_now=True,verbose_name="诊断项更新时间")

    diagnosis = models.ForeignKey(Diagnosis,on_delete=models.PROTECT,verbose_name="诊断",related_name="items")

    pathologyPicture = models.ForeignKey(PathologyPictureItem,on_delete=models.PROTECT,verbose_name="病理图片")
    
    
    class Meta:
        verbose_name = '诊断项'
        verbose_name_plural = '诊断项集'


class LabelItem(models.Model):
    MUSHROOM = 'M'
    CATEGORY_CHOICES = [
        (MUSHROOM, '真菌')
    ]
    id = models.UUIDField(primary_key=True,default=uuid4)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="标注时间")
    modifiedAt = models.DateTimeField(auto_now=True,verbose_name="标注更新时间")
    diagnosisItem = models.ForeignKey(DiagnosisItem,on_delete=models.PROTECT,verbose_name="诊断项")
    category = models.CharField(
        max_length=4, choices=CATEGORY_CHOICES, default=MUSHROOM,verbose_name="类别")
    x = models.FloatField(verbose_name="标注起点坐标X")
    y = models.FloatField(verbose_name="标注起点坐标Y")
    w = models.FloatField(verbose_name="标注宽度")
    h = models.FloatField(verbose_name="标注高度")
    zoomLevel = models.FloatField(default=10.0,verbose_name="标注时放大倍数")
    regionPicture = models.FileField(blank=True,null=True,verbose_name="标注区域图")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,verbose_name="医生")
    confidence = models.FloatField(default=1.0,verbose_name="自信度")
    
    @admin.display(description="诊断ID")
    def getDiagnosisItem(self):
        return self.diagnosisItem.id
    class Meta:
        verbose_name = '标注'
        verbose_name_plural = '标注集'