from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from .models import PathologyPictureItem,LabelItem,DiagnosisItem,Diagnosis,Patient, Report
class PathologyPictureItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = PathologyPictureItem
        fields = ["id","pathologyPicture","createdAt","patient","description"]
class DiagnosisItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DiagnosisItem
        fields = ["id","diagnosis","pathologyPicture","createdAt"]
    pathologyPicture = PathologyPictureItemSerializer()
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id","name","age",'sex']
    
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ["id","patient","createdAt",'items']
    patient = PatientSerializer()
    items=DiagnosisItemSerializer(many=True,read_only=True)
class DiagnosisPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Diagnosis
        fields = ["isFinished"]
class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ["id","username"]
class LabelItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=LabelItem
        fields=['id','createdAt','modifiedAt','category','x','y','w','h','zoomLevel','doctor','confidence']
    doctor = DoctorSerializer(read_only=True)
        

    def create(self, validated_data):
        diagnosisItem_id = self.context['diagnosisitem_pk']
        doctor = self.context['doctor']
        return LabelItem.objects.create(diagnosisItem_id=diagnosisItem_id,doctor=doctor,**validated_data)
class ReportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Report
        fields = ["id","diagnosis","labelitems","modifiedAt","createdAt"]
class ReportPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Report
        fields = ["labelitems"]
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)