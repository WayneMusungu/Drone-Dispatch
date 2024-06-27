from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dispatch.models import Drone, Medication

class RegisterDroneViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('register_drone')
        self.valid_payload = {
            'serial_number': 'XTY-899',
            'model': 'LIGHTWEIGHT',
            'weight_limit': 200,
            'battery_capacity': 75.0,
            'state': 'IDLE'
        }
        self.duplicate_payload_serial_number = {
            'serial_number': 'XTY-899',  # Duplicate serial number
            'model': 'MIDDLEWEIGHT',
            'weight_limit': 500, 
            'battery_capacity': 75.0,
            'state': 'IDLE'
        }
        self.invalid_weight_limit = {
            'serial_number': 'PXR-890',  
            'model': 'MIDDLEWEIGHT',
            'weight_limit': 600, # Invalid weight limit
            'battery_capacity': 75.0,
            'state': 'IDLE'
        }
        self.invalid_model_choice = {
            'serial_number': 'PFF-990',  
            'model': 'LIGHT', # Invalid model choice
            'weight_limit': 400, 
            'battery_capacity': 75.0,
            'state': 'IDLE'
        }

    def tearDown(self):
        Drone.objects.all().delete()

    def test_register_drone_success(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Drone.objects.count(), 1)

        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['medications'], [])
        self.assertEqual(response.data['serial_number'], 'XTY-899')
        self.assertEqual(response.data['model'], 'LIGHTWEIGHT')
        self.assertEqual(response.data['weight_limit'], 200)
        self.assertEqual(response.data['battery_capacity'], 75.0)
        self.assertEqual(response.data['state'], 'IDLE')
        
    def test_register_drone_duplicate_serial_number(self):
        # Register a drone with valid_payload first
        self.client.post(self.url, self.valid_payload, format='json')
        response = self.client.post(self.url, self.duplicate_payload_serial_number, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Asses the first error message in the list
        self.assertEqual(response.data['serial_number'][0], 'drone with this serial number already exists.')

    def test_register_drone_invalid_weight(self):
        # Register a drone with valid_payload first
        response = self.client.post(self.url, self.invalid_weight_limit, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['weight_limit'][0], 'Ensure this value is less than or equal to 500.')
        
    def test_register_drone_invalid_model(self):
        # Register a drone with valid_payload first
        response = self.client.post(self.url, self.invalid_model_choice, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['model'][0], '"LIGHT" is not a valid choice.')


class LoadMedicationViewAPITest(APITestCase):
    def setUp(self):
        self.drone = Drone.objects.create(
            state='IDLE',
            battery_capacity=50,
            weight_limit=500
        )
        
    def tearDown(self):
        self.drone.delete()
        
    def test_load_medication_sucess(self):
        url = reverse('load_medication', kwargs={'pk': self.drone.pk})
        payload = {
            'medications': [
                {'name': 'Medicine A', 'weight': 200, 'code':'TRM500'},
                {'name': 'Medicine B', 'weight': 300, 'code':'XXL390'},
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Medications loaded successfully')
        self.assertIn('medications', response.data)
        self.assertEqual(len(response.data['medications']), 2)  
        
    def test_load_medications_drone_not_found(self):
        url = reverse('load_medication', kwargs={'pk': 999})
        payload = {
            'medications': [
                {'name': 'Medicine A', 'weight': 20, 'code':'TRM500'},
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'Drone not found')
        
    def test_load_medications_invalid_state(self):
        self.drone.state = 'LOADED'
        self.drone.save()
        url = reverse('load_medication', kwargs={'pk': self.drone.pk})
        payload = {
            'medications': [
                {'name': 'Medicine A', 'weight': 20, 'code':'TRM500'},
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'Drone must be in IDLE or LOADING state to start loading medications')
