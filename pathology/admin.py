from django.contrib import admin

from django.conf import settings
from django.apps import apps
from django.db.models.aggregates import Count

from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models


admin.site.site_header = "苏州海康华智病理辅助诊断工作站"
admin.site.site_title = "病理辅助诊断"


@admin.register(models.PathologyPictureItem)
class PathologyPictureAdmin(admin.ModelAdmin):
    list_display = ['id','patient_name','createdAt','description','pathologyPicture','isCutted','startDignose','generateDignoseDoc']
    autocomplete_fields = ['patient']
    ordering = ['createdAt']
    list_per_page = 10
    list_select_related = ['patient']
    search_fields = ['description']

    @admin.display(description="患者")
    def patient_name(self, pathologyPictureItem):
        return pathologyPictureItem.patient.name
    
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
    list_display = ['name','sex','age','diagnoses_count']
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

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            diagnoses_count=Count('diagnoses')
        )
    

@admin.register(models.LabelItem)
class LabelItemAdmin(admin.ModelAdmin):
    list_display = ['id','getPathologyPictureItemId','x','y','w','h','category','regionPicture']

class DiagnosisItemInline(admin.TabularInline):
    autocomplete_fields = ['pathologyPicture']
    min_num = 1
    max_num = 10
    model = models.DiagnosisItem
    extra = 0
@admin.register(models.Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    autocomplete_fields = ['patient']
    list_display = ['id','patient','doctorNames','isFinished','last_update','createdAt']
    inlines = [DiagnosisItemInline]
    search_fields = ['patient__name']

    filter_horizontal = (
        'doctors',
    )
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "doctors":
            kwargs["queryset"] = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(groups__name='普通医生')
        
        field = super(DiagnosisAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        
        return field