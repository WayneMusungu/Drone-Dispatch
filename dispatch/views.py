from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from dispatch.models import Drone, Medication
from dispatch.serializers import AvailableDroneSerializer, DroneLodedMedicationSerializer, DroneSerializer, MedicationSerializer



# Create your views here.

class RegisterDroneView(generics.CreateAPIView):
    q_set = Drone.objects.all()
    serializer_class = DroneSerializer
    
class LoadMedicationView(APIView):
    serializer_class = MedicationSerializer

    def post(self, request, id):
        try:
            drone = Drone.objects.get(id=id)
        except Drone.DoesNotExist:
            return Response({'status': 'Drone not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check drone state and battery level
        if drone.state not in ['IDLE', 'LOADING']:
            return Response({'status': 'Drone must be in IDLE or LOADING state to start loading medications'}, status=status.HTTP_400_BAD_REQUEST)
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
        try:
            with transaction.atomic():
                medications_created = []
                for med_data in medications_data:
                    med_data['drone'] = id
                    serializer = self.serializer_class(data=med_data)
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

            remaining_weight = drone.weight_limit - (total_weight + current_weight)

            return Response({
                'status': 'Medications loaded successfully',
                'medications': medications_created,
                'remaining_weight': remaining_weight
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': False,
                'message': 'Unexpected error occurred!',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        

class CheckLoadedMedicationsView(APIView):
    serializer_class = MedicationSerializer

    def get(self, request, id):
        try:
            drone = Drone.objects.get(id=id)
        except Drone.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Drone does not exist',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # Catch any other exceptions, such as database errors
            return Response({
                'status': False,
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        medications = Medication.objects.filter(drone=drone)
        medication_serializer = self.serializer_class(medications, many=True)
        drone_serializer = DroneLodedMedicationSerializer(drone)

        if medications.exists():
            return Response({
                'status': True,
                'drone': drone_serializer.data,
                'medications': medication_serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': True,
                'drone': drone_serializer.data,
                'message': 'This drone has no medications associated with it',
                'medications': medication_serializer.data
            }, status=status.HTTP_200_OK)
            
            
class AvailableDronesForLoadingView(APIView):
    serializer_class = AvailableDroneSerializer

    def get(self, request):
        available_drones = Drone.objects.filter(state='IDLE', battery_capacity__gte=25)  # Use greater or equal to include drones with 25% battery or more
        serializer = self.serializer_class(available_drones, many=True)
        
        return Response({
            'status': 'Success',
            'available_drones': serializer.data
        }, status=status.HTTP_200_OK)           
            
            
class CheckDroneBatteryLevelView(APIView):

    def get(self, request, id):
        try:
            drone = Drone.objects.get(id=id)
        except Drone.DoesNotExist:
            return Response({
                'status': 'Drone not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'Success',
            'id': drone.id,
            'drone_serial_number':drone.serial_number,
            'battery_level': drone.battery_capacity
        }, status=status.HTTP_200_OK)