from rest_framework import serializers
from .models import Drone, Medication

class DroneSerializer(serializers.ModelSerializer):
    medications = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Drone
        fields = '__all__'
        

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'