from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from dispatch.models import Drone, Medication
from dispatch.serializers import DroneSerializer, MedicationSerializer



# Create your views here.

class RegisterDroneView(generics.CreateAPIView):
    q_set = Drone.objects.all()
    serializer_class = DroneSerializer
    
class LoadMedicationView(generics.GenericAPIView):
    serializer_class = MedicationSerializer

    def post(self, request, *args, **kwargs):
        drone_id = kwargs.get('pk')
        try:
            drone = Drone.objects.get(pk=drone_id)
        except Drone.DoesNotExist:
            return Response({'status': 'Drone not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check drone state and battery level
        if drone.state != 'IDLE':
            return Response({'status': 'Drone must be in IDLE state to start loading medications'}, status=status.HTTP_400_BAD_REQUEST)
        if drone.battery_capacity < 25:
            return Response({'status': 'Battery level is below 25%'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate payload for medications
        medications_data = request.data.get('medications', [])
        if not medications_data:
            return Response({'status': 'No medications specified'}, status=status.HTTP_400_BAD_REQUEST)

        total_weight = sum(med_data.get('weight', 0) for med_data in medications_data)
        current_weight = Medication.objects.filter(drone=drone).aggregate(total_weight=Sum('weight'))['total_weight'] or 0
        
        if total_weight + current_weight > drone.weight_limit:
            return Response({'status': 'Total weight exceeds drone weight limit'}, status=status.HTTP_400_BAD_REQUEST)

        # Use transaction.atomic to ensure atomicity
        with transaction.atomic():
            # Create medications and associate with the drone
            medications_created = []
            for med_data in medications_data:
                # Assign drone ID to each medication data
                med_data['drone'] = drone_id
                serializer = MedicationSerializer(data=med_data)
                if serializer.is_valid():
                    serializer.save()
                    medications_created.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Update drone state based on total weight loaded
            if total_weight + current_weight == drone.weight_limit:
                drone.state = 'LOADED'  
            else:
                drone.state = 'LOADING'
            drone.save()

        return Response({'status': 'Medications loaded successfully', 'medications': medications_created}, status=status.HTTP_200_OK)
    
    
