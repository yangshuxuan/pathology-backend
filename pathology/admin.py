from django.contrib import admin
from django.utils.html import format_html,urlencode
from django.conf import settings
from . import models


#register link
# admin.site.site_url = "/media/renameSample.py"
# admin.site.site_header="help"
# Register your models here.

@admin.register(models.PathologyPictureItem)
class PathologyPictureAdmin(admin.ModelAdmin):
    list_display = ['id','patient_name','createdAt','description','pathologyPicture','isCutted','startDignose']
    autocomplete_fields = ['patient']
    ordering = ['createdAt']
    list_per_page = 10
    list_select_related = ['patient']
    # search_fields = ['title']

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
        


class PathologyPictureInline(admin.StackedInline):
    model = models.PathologyPictureItem
    extra = 0

@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name','sex','age']
    inlines = [PathologyPictureInline]
    search_fields = ['name']