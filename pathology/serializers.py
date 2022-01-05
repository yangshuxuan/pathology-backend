from rest_framework import serializers
from .models import PathologyPictureItem,LabelItem,DiagnosisItem,Diagnosis
class PathologyPictureItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = PathologyPictureItem
        fields = ["id","pathologyPicture","createdAt","patient","description"]
class DiagnosisItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = DiagnosisItem
        fields = ["id","diagnosis","pathologyPicture","createdAt"]
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ["id","patient","createdAt",'items']
    items=DiagnosisItemSerializer(many=True,read_only=True)
class LabelItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=LabelItem
        fields=['id','createdAt','modifiedAt','category','x','y','w','h','zoomLevel']
        

    def create(self, validated_data):
        diagnosisItem_id = self.context['diagnosisitem_pk']
        return LabelItem.objects.create(diagnosisItem_id=diagnosisItem_id,**validated_data)
    