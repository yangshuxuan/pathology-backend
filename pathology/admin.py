from django.contrib import admin

from django.conf import settings
from django.apps import apps
from django.db.models.aggregates import Count

from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.utils.safestring import mark_safe
from . import models


admin.site.site_header = "苏州海康华智病理辅助诊断工作站"
admin.site.site_title = "病理辅助诊断"


@admin.register(models.PathologyPictureItem)
class PathologyPictureAdmin(admin.ModelAdmin):
    list_display = ['id','show_patient','createdAt','description','pathologyPicture','isCutted','startDignose','generateDignoseDoc']
    autocomplete_fields = ['patient']
    ordering = ['createdAt']
    list_per_page = 10
    list_select_related = ['patient']
    search_fields = ['description']

    
    @admin.display(description="患者")
    def show_patient(self, pathologyPictureItem):
        url = (
            reverse('admin:pathology_patient_changelist')
            + '?'
            + urlencode({
                'id': str(pathologyPictureItem.patient.id)
            }))
        return format_html('<a href="{}">{}</a>', url, pathologyPictureItem.patient.name)
    @admin.display(description="开始诊断")
    def startDignose(self,pathologyPictureItem):
        if pathologyPictureItem.isCutted:
            base_url = "http://localhost:3000"
            # query_string =  urlencode({'pathologyPictureItem': pathologyPictureItem.id})  # 2 category=42
            url = '{}/{}'.format(base_url, pathologyPictureItem.id)
            return format_html('<a href="{}"><img src="{}pathology/explorer.svg" width="25" height="20" alt="诊断"></a>',url,settings.STATIC_URL)
    @admin.display(description="诊断报告")
    def generateDignoseDoc(self,patient):
        base_url = "/pathology/generatedoc"
        query_string =  urlencode({'patient__id': patient.id})  
        url = '{}?{}'.format(base_url, query_string)
        return format_html('<a href="{}"><img src="{}pathology/explorer.svg" width="25" height="20" alt="浏览"></a>',url,settings.STATIC_URL)    


class DiagnosisInline(admin.StackedInline):
    model = models.Diagnosis

    fields = ("doctors", "description")

    filter_horizontal = (
        'doctors',
    )
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "doctors":
            kwargs["queryset"] = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(groups__name='普通医生')
        
        field = super(DiagnosisInline, self).formfield_for_manytomany(db_field, request, **kwargs)
        
        return field
    extra = 0



@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name','pathologypicture_count','diagnoses_count','sex','age']
    inlines = [DiagnosisInline]
    search_fields = ['name']

    @admin.display(ordering='diagnoses_count',description="诊断数")
    def diagnoses_count(self, patient):
        url = (
            reverse('admin:pathology_diagnosis_changelist')
            + '?'
            + urlencode({
                'patient__id': str(patient.id)
            }))
        return format_html('<a href="{}">{} 诊断</a>', url, patient.diagnoses_count)
    @admin.display(ordering='pathologypicture_count',description="病理图片数")
    def pathologypicture_count(self, patient):
        url = (
            reverse('admin:pathology_pathologypictureitem_changelist')
            + '?'
            + urlencode({
                'patient__id': str(patient.id)
            }))
        return format_html('<a href="{}">{} 病理图片</a>', url, patient.pathologypicture_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            pathologypicture_count=Count('pathologypictures',distinct=True)).annotate(
            diagnoses_count=Count('diagnoses',distinct=True)
        )
        # 'pathologypicture_count',,pathologypicture_count=Count('pathologypictures')
        
    

@admin.register(models.LabelItem)
class LabelItemAdmin(admin.ModelAdmin):
    list_display = ['id','getDiagnosisItem','x','y','w','h','category','doctor_name','confidence','showRegionPicture']
    @admin.display(description="医生")
    def doctor_name(self, labelItem):
        return labelItem.doctor.username
    @admin.display(description="标注区域图")
    def showRegionPicture(self, labelItem):
        # return mark_safe('<img src="{url}" />'.format(url = labelItem.regionPicture.url)
        width = 200
        # if obj and obj.pathologyPicture  and obj.pathologyPicture.size <= 10 *1024 * 1024  :
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = labelItem.regionPicture.url,
            width=width,
            height=1.0 * labelItem.regionPicture.height/labelItem.regionPicture.width * width,
        )
    )

class DiagnosisItemInline(admin.TabularInline):
    autocomplete_fields = ['pathologyPicture']
    min_num = 1
    max_num = 10
    model = models.DiagnosisItem
    extra = 0
@admin.register(models.Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    autocomplete_fields = ['patient']
    list_display = ['id','show_patient','doctorNames','diagnosisitem_count','isFinished','last_update','createdAt']
    inlines = [DiagnosisItemInline]
    search_fields = ['patient__name']
    @admin.display(description="患者")
    def show_patient(self, diagnosis):
        url = (
            reverse('admin:pathology_patient_changelist')
            + '?'
            + urlencode({
                'id': str(diagnosis.patient.id)
            }))
        return format_html('<a href="{}">{}</a>', url, diagnosis.patient.name)

    filter_horizontal = (
        'doctors',
    )
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "doctors":
            kwargs["queryset"] = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(groups__name='普通医生')
        
        field = super(DiagnosisAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        
        return field
    @admin.display(ordering='diagnoses_count',description="诊断项数")
    def diagnosisitem_count(self, diagnosis):
        url = (
            reverse('admin:pathology_diagnosisitem_changelist')
            + '?'
            + urlencode({
                'diagnosis__id': str(diagnosis.id)
            }))
        return format_html('<a href="{}">{} 诊断项</a>', url, diagnosis.diagnosisitem_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            diagnosisitem_count=Count('items')
        )

@admin.register(models.DiagnosisItem)
class DiagnosisItemAdmin(admin.ModelAdmin):
    list_display = ['id','show_diagnosis','show_pathologyPicture','labelitem_count','last_update','createdAt']
    @admin.display(description="病理图片ID")
    def show_pathologyPicture(self, diagnosisItem):
        url = (
            reverse('admin:pathology_pathologypictureitem_changelist')
            + '?'
            + urlencode({
                'id': str(diagnosisItem.pathologyPicture.id)
            }))
        return format_html('<a href="{}">{}</a>', url, diagnosisItem.pathologyPicture.id)
    @admin.display(description="诊断ID")
    def show_diagnosis(self, diagnosisItem):
        url = (
            reverse('admin:pathology_diagnosis_changelist')
            + '?'
            + urlencode({
                'id': str(diagnosisItem.diagnosis.id)
            }))
        return format_html('<a href="{}">{}</a>', url, diagnosisItem.diagnosis.id)
    @admin.display(ordering='labelitem_count',description="标注项数")
    def labelitem_count(self, diagnosisItem):
        url = (
            reverse('admin:pathology_labelitem_changelist')
            + '?'
            + urlencode({
                'diagnosisItem__id': str(diagnosisItem.id)
            }))
        return format_html('<a href="{}">{} 标注项</a>', url, diagnosisItem.labelitem_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            labelitem_count=Count('items')
        )
    