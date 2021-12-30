
from django.shortcuts import get_object_or_404
import xml.etree.ElementTree as ET
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from pathology.tasks import readImage
from .models import PathologyPictureItem,LabelItem
from .serializers import PathologyPictureItemSerializer,LabelItemSerializer
from rest_framework.decorators import action
from pathlib import PurePath
from urllib.parse import urlparse
from django.utils.encoding import escape_uri_path

from django.http import HttpResponseBadRequest
from docxtpl import DocxTemplate,RichText
from django.conf import settings
from  django.http import HttpResponse
from io import BytesIO
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
# Create your views here.

class PathologyPictureItemViewSet(ModelViewSet):
    queryset = PathologyPictureItem.objects.all()
    serializer_class = PathologyPictureItemSerializer

    @action(detail=True)
    def history(self,request,pk):
        pathologyPictureItem = PathologyPictureItem.objects.get(pk=pk)
        f = PurePath(pathologyPictureItem.pathologyPicture.name)
        v = f"{f.stem}.dzi"
        readImage(v)
        tree = ET.parse(v)
        root = tree.getroot()
        o=urlparse(pathologyPictureItem.pathologyPicture.url)
        url = o._replace(path=str( f"{f.stem}_files/")).geturl()

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
        get_object_or_404(PathologyPictureItem,pk=self.kwargs["pathologypictureitem_pk"])
        return LabelItem.objects.filter(pathologypictureitem_id=self.kwargs["pathologypictureitem_pk"])
        
    def get_serializer_context(self):
        return {"pathologypictureitem_pk":self.kwargs["pathologypictureitem_pk"]}

def checkedElement():
    elm = OxmlElement('w:checked')
    elm.set(qn('w:val'),"true")
    return elm
def generateDocument(request):
    patientId = request.GET.get("patient__id")
    
    p = get_object_or_404(PathologyPictureItem, pk=patientId)
    # if p.doctors.filter(id = request.user.id).exists():
    docx_title=f"{patientId}诊断报告.docx"
    tpl = DocxTemplate(settings.BASE_DIR / 'template.docx')
    rt = RichText('w:checked')
    # rt.add('google',url_id=tpl.build_url_id('http://google.com'))

    context = {
        'name':rt,
        
    }

    tpl.render(context)
    


    

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
