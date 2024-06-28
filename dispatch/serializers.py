from rest_framework import serializers
from .models import Drone, Medication
from django.db.models import Sum


class DroneSerializer(serializers.ModelSerializer):
    medications = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Drone
        fields = '__all__'
        

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        
        
class DroneLodedMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = ['id','serial_number']
        

class AvailableDroneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Drone
        fields = ['id', 'serial_number', 'model', 'weight_limit', 'battery_capacity', 'state']