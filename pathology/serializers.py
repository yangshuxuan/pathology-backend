from rest_framework import serializers
from .models import PathologyPictureItem,LabelItem
class PathologyPictureItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = PathologyPictureItem
        fields = ["id","pathologyPicture","createdAt","patient","description"]

class LabelItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=LabelItem
        fields=['id','createdAt','modifiedAt','category','x','y','w','h','zoomLevel']
        

    def create(self, validated_data):
        pathologypictureitem_id = self.context['pathologypictureitem_pk']
        return LabelItem.objects.create(pathologypictureitem_id=pathologypictureitem_id,**validated_data)
    