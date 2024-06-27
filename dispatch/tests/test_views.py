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
        response = self.client.post(self.url, self.invalid_weight_limit, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['weight_limit'][0], 'Ensure this value is less than or equal to 500.')
        
    def test_register_drone_invalid_model(self):
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
        url = reverse('load_medication', kwargs={'id': self.drone.id})
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
        url = reverse('load_medication', kwargs={'id': 999})
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
        url = reverse('load_medication', kwargs={'id': self.drone.id})
        payload = {
            'medications': [
                {'name': 'Medicine A', 'weight': 20, 'code':'TRM500'},
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'Drone must be in IDLE or LOADING state to start loading medications')
        
        
        
class CheckLoadedMedicationsViewTest(APITestCase):
    def setUp(self):
        
        self.drone = Drone.objects.create(
            serial_number='XTY-899',
            model='LIGHTWEIGHT',
            weight_limit=200,
            battery_capacity=75.0,
            state='IDLE'
        )

        """ Create medications associated with the drone"""
        self.medication1 = Medication.objects.create(
            name='Med1',
            weight=10,
            code='TTY-908',
            drone=self.drone
        )
        self.medication2 = Medication.objects.create(
            name='Med2',
            weight=5,
            code='XGF-001',
            drone=self.drone
        )

        self.url = reverse('loaded_medications', kwargs={'id': self.drone.id})
        
    def tearDown(self):
        Drone.objects.all().delete()
        Medication.objects.all().delete()

    def test_loaded_medications_exists(self):
        """Test case where medications exist for the drone"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(len(response.data['medications']), 2)

    def test_loaded_medications_not_exist(self):
        """Test case where no medications exist for the drone"""
        Medication.objects.filter(drone=self.drone).delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(response.data['message'], 'This drone has no medications associated with it')
        self.assertEqual(response.data.get('medications', []), [])

    def test_loaded_medications_drone_not_found(self):
        """ Test case where drone does not exist"""
        invalid_url = reverse('loaded_medications', kwargs={'id': self.drone.id + 1})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['message'], 'Drone does not exist')
        
              
class CheckDroneBatteryLevelViewTest(APITestCase):
    def setUp(self):
        self.drone = Drone.objects.create(
            serial_number='XTY-899',
            model='LIGHTWEIGHT',
            weight_limit=200,
            battery_capacity=75.0,
            state='IDLE'
        )
        self.url = reverse('check_drone_battery', kwargs={'id': self.drone.id})
        
    def tearDown(self):
        Drone.objects.all().delete()

    def test_check_drone_battery_level_success(self):
        """Test case where drone exists"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Success')
        self.assertEqual(response.data['drone_id'], self.drone.id)
        self.assertEqual(response.data['drone_serial_number'], self.drone.serial_number)
        self.assertEqual(response.data['battery_level'], self.drone.battery_capacity)

    def test_check_drone_battery_level_not_found(self):
        """Test case where drone does not exist"""
        invalid_url = reverse('check_drone_battery', kwargs={'id': self.drone.id + 1})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'Drone not found')

   

   
