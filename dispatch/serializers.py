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
    # remaining_weight = serializers.SerializerMethodField()

    class Meta:
        model = Drone
        fields = ['id', 'serial_number', 'model', 'weight_limit', 'battery_capacity', 'state']

    # def get_remaining_weight(self, obj):
    #     current_weight = obj.medications.aggregate(total_weight=Sum('weight'))['total_weight'] or 0
    #     return obj.weight_limit - current_weight