
from django.shortcuts import get_object_or_404
import xml.etree.ElementTree as ET
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import PathologyPictureItem,LabelItem
from .serializers import PathologyPictureItemSerializer,LabelItemSerializer
from rest_framework.decorators import action
from pathlib import PurePath
from django.utils.encoding import escape_uri_path

# Create your views here.

class PathologyPictureItemViewSet(ModelViewSet):
    queryset = PathologyPictureItem.objects.all()
    serializer_class = PathologyPictureItemSerializer

    @action(detail=True)
    def history(self,request,pk):
        pathologyPictureItem = PathologyPictureItem.objects.get(pk=pk)
        f = PurePath(pathologyPictureItem.pathologyPicture.path)
        v = f.parent / f"{f.stem}.dzi"
        tree = ET.parse(str(v))
        root = tree.getroot()

        data = {
            "Image": {
                "xmlns": "http://schemas.microsoft.com/deepzoom/2009",
                "Url": f"{request.build_absolute_uri('/')}media/{escape_uri_path(f.stem)}_files/",
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