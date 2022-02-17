
from django.shortcuts import get_object_or_404
import xml.etree.ElementTree as ET
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from pathology.tasks import readImageDzi
from .models import PathologyPictureItem,LabelItem,DiagnosisItem,Diagnosis, Report
from .serializers import PathologyPictureItemSerializer,LabelItemSerializer,DiagnosisItemSerializer,DiagnosisSerializer,DiagnosisPatchSerializer,ReportSerializer,ReportPatchSerializer
from rest_framework.decorators import action

from urllib.parse import urlparse
from django.utils.encoding import escape_uri_path
from django.db.models import Q
from .tasks import readRegionImage

from django.conf import settings
from  django.http import HttpResponse
from io import BytesIO
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
from django_filters.rest_framework import DjangoFilterBackend
from docxtpl import DocxTemplate, InlineImage,RichText

# for height and width you have to use millimeters (Mm), inches or points(Pt) class :
from docx.shared import Mm
import jinja2
# Create your views here.

class PathologyPictureItemViewSet(ModelViewSet):
    queryset = PathologyPictureItem.objects.all()
    serializer_class = PathologyPictureItemSerializer

class DiagnosisViewSet(ModelViewSet):
    # queryset = Diagnosis.objects.select_related("patient").prefetch_related("items__pathologyPicture").all()
    serializer_class = DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['isFinished']
    def get_serializer_class(self):
        if self.request.method=="PATCH":
            return DiagnosisPatchSerializer
        else:
            return DiagnosisSerializer
    def get_queryset(self):
        user = self.request.user
        queryset = Diagnosis.objects.select_related("patient").prefetch_related("items__pathologyPicture")
        if not user.is_anonymous :
            queryset = queryset.filter(Q(doctors=user)) 
        return queryset
class DiagnosisItemViewSet(ModelViewSet):
    queryset = DiagnosisItem.objects.all()
    serializer_class = DiagnosisItemSerializer
    @action(detail=True)
    def image_detail(self,request,pk):
        pathologyPictureItem = DiagnosisItem.objects.get(pk=pk).pathologyPicture
        
        v = str(readImageDzi(pathologyPictureItem))
        
        tree = ET.parse(v)
        root = tree.getroot()
        o=urlparse(pathologyPictureItem.pathologyPicture.url)

        fileName = Path(pathologyPictureItem.pathologyPicture.name).stem
        remoteCuttedFiles=str(Path(settings.AWS_LOCATION,settings.CUTTED_IMAGES_LOCATION) / f"{fileName}_files")
        url = o._replace(path=str( f"{remoteCuttedFiles}/")).geturl()

        data = {
            "Image": {
                "xmlns": "http://schemas.microsoft.com/deepzoom/2009",
                "Url": url,
                "Overlap": root.get("Overlap"),
                "TileSize": root.get("TileSize"),
                "Format": root.get("Format"),
                "Size": {
                    "Height": root[0].get('Height'),
                    "Width": root[0].get('Width'),
                },
            }
        }
        
        return Response(data)


class LabelItemViewSet(ModelViewSet):
    serializer_class = LabelItemSerializer
    def get_queryset(self):
        diagnosisItem = get_object_or_404(DiagnosisItem,pk=self.kwargs["diagnosisitem_pk"])
        others = self.request.query_params.get('others')
        if others == 'true':
            return LabelItem.objects.filter(
                diagnosisItem__pathologyPicture__id=diagnosisItem.pathologyPicture.id
                ).exclude(diagnosisItem_id=self.kwargs["diagnosisitem_pk"])
        return LabelItem.objects.filter(diagnosisItem_id=self.kwargs["diagnosisitem_pk"])
        
    def get_serializer_context(self):
        
        return {"diagnosisitem_pk":self.kwargs["diagnosisitem_pk"],"doctor":self.request.user}
class ReportViewSet(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['diagnosis_id']
    # def get_serializer_class(self):
    #     if self.request.method=="PATCH":
    #         return ReportPatchSerializer
    #     else:
    #         return ReportSerializer
def checkedElement():
    elm = OxmlElement('w:checked')
    elm.set(qn('w:val'),"true")
    return elm
def generateDocument(request):
    reportId = request.GET.get("report__id")
    
    report = get_object_or_404(Report, pk=reportId)
    # if p.doctors.filter(id = request.user.id).exists():
    docx_title=f"{report.diagnosis.patient.name}诊断报告.docx"
    tpl = DocxTemplate(settings.BASE_DIR / 'template.docx')
    rt = RichText('w:checked')
    # rt.add('google',url_id=tpl.build_url_id('http://google.com'))
    images = [InlineImage(tpl, str(readRegionImage(lableitem)), height=Mm(30)) for lableitem in report.labelitems.all()]

    allimages=[]
    t = []
    i = 0
    v = 3
    for image in images:
        i+=1
        t.append(image)
        if i % v ==0:
            i=0
            allimages.append(t)
            t=[]
    if i!=0:
        allimages.append(t)
    
    manyi = u"\u2611" if report.manyi else u"\u2610"
    jinguanxibao  = u"\u2611" if report.jinguanxibao else u"\u2610"
    huashengxibao  = u"\u2611" if report.huashengxibao else u"\u2610"
    bumanyi  = u"\u2611" if report.bumanyi else u"\u2610"
    M = u"\u2611" if report.M else u"\u2610"
    TR = u"\u2611" if report.TR else u"\u2610"
    AM = u"\u2611" if report.AM else u"\u2610"
    CL = u"\u2611" if report.CL else u"\u2610"
    CMV = u"\u2611" if report.CMV else u"\u2610"
    HSV = u"\u2611" if report.HSV else u"\u2610"
    IM = u"\u2611" if report.IM else u"\u2610"
    S = u"\u2611" if report.S else u"\u2610"
    ASC_US = u"\u2611" if report.ASC_US else u"\u2610"
    ASC_H = u"\u2611" if report.ASC_H else u"\u2610"
    AGC_NSL_CC = u"\u2611" if report.AGC_NSL_CC else u"\u2610"
    AGC_NSL_E = u"\u2611" if report.AGC_NSL_E else u"\u2610"
    AGC_NSL_US = u"\u2611" if report.AGC_NSL_US else u"\u2610"
    LSIL = u"\u2611" if report.LSIL else u"\u2610"
    AGC_FN_CC = u"\u2611" if report.AGC_FN_CC else u"\u2610"
    AGC_FN_US = u"\u2611" if report.AGC_FN_US else u"\u2610"
    HSIL = u"\u2611" if report.HSIL else u"\u2610"
    AIS = u"\u2611" if report.AIS else u"\u2610"
    SCC = u"\u2611" if report.SCC else u"\u2610"
    GC_CC = u"\u2611" if report.GC_CC else u"\u2610"
    GC_E = u"\u2611" if report.GC_E else u"\u2610"
    GC_OT = u"\u2611" if report.GC_OT else u"\u2610"
    OTHER = u"\u2611" if report.OTHER else u"\u2610"
    

    context = {
        'name':rt,
        "manyi":manyi,
        "jinguanxibao":jinguanxibao,
        "huashengxibao":huashengxibao,
        "bumanyi":bumanyi,
        "M":M,
        "TR":TR,
        "AM":AM,
        "CL":CL,
        "CMV":CMV,
        "HSV":HSV,
        "IM":IM,
        "S":S,
        "ASC_US":ASC_US,
        "ASC_H":ASC_H,
        "AGC_NSL_CC":AGC_NSL_CC,
        "AGC_NSL_E":AGC_NSL_E,
        "AGC_NSL_US":AGC_NSL_US,
        "LSIL":LSIL,
        "AGC_FN_CC":AGC_FN_CC,
        "AGC_FN_US":AGC_FN_US,
        "HSIL":HSIL,
        "AIS":AIS,
        "SCC":SCC,
        "GC_CC":GC_CC,
        "GC_E":GC_E,
        "GC_OT":GC_OT,
        "OTHER":OTHER,
        "advice":report.advice,
        'allimages':allimages
        
    }
    jinja_env = jinja2.Environment(autoescape=True)
    tpl.render(context, jinja_env)

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    tpl.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(docx_title)}'
    response['Content-Length'] = length
    return response
