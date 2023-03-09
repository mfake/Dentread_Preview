from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from .models import IOSFile, FeedFile, RadiologycalServices, ImageAnalysis, ImplantPlanning, Suricalguide, DesignFile, Notification, LabItem, LabMaterial, LabOrderItem, AddOnLabServices
from .models import SubMaterial, ServiceOrder, OtherImageFile

class OtherImageFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = OtherImageFile
        fields = '__all__'
class LabItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = LabItem
        fields = '__all__'

class LabMaterialSerializers(serializers.ModelSerializer):
    class Meta:
        model = LabMaterial
        fields = '__all__'

class LabOrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = LabOrderItem
        fields = '__all__'

class AddOnLabServicesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AddOnLabServices
        fields = '__all__'
    
class IOSFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = IOSFile
        fields = '__all__'

class NotificationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FeedFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = FeedFile
        fields = '__all__'

class DesignFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = DesignFile
        fields = '__all__'

class RadiologycalSerializers(serializers.ModelSerializer):
    class Meta:
        model = RadiologycalServices
        fields = '__all__'

class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ImageAnalysis
        fields = '__all__'

class ImplantSerializers(serializers.ModelSerializer):
    class Meta:
        model = ImplantPlanning
        fields = '__all__'

class GuideSerializers(serializers.ModelSerializer):
    class Meta:
        model = Suricalguide
        fields = '__all__'

class SubMaterialSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubMaterial
        fields = '__all__'
        
class ServiceOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = '__all__'