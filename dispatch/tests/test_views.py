from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from dispatch.models import Drone, Medication
from PIL import Image
import io

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
        
        """ Create a valid in-memory image"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=image_file.read(), content_type='image/jpeg')
        
        self.payload = {
            'name': 'Medicine A',
            'weight': 20,
            'code': 'TRM500',
            'image': self.image
        }
        
    def tearDown(self):
        Medication.objects.filter(drone=self.drone).delete()
        self.drone.delete()
        
    def test_load_medication_success(self):
        url = reverse('load_medication', kwargs={'id': self.drone.id})
        
        response = self.client.post(url, self.payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Medication loaded successfully')
        self.assertIn('medication', response.data)
        
        """ Verify that only one medication was created"""
        medications = Medication.objects.filter(drone=self.drone)
        self.assertEqual(medications.count(), 1)
        
    def test_load_medications_drone_not_found(self):
        url = reverse('load_medication', kwargs={'id': 999})
    
        response = self.client.post(url, self.payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'Drone not found')
        
    def test_load_medications_invalid_state(self):
        self.drone.state = 'LOADED'
        self.drone.save()
        url = reverse('load_medication', kwargs={'id': self.drone.id})
     
        response = self.client.post(url, self.payload, format='multipart')
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
        
              
class AvailableDronesForLoadingViewTest(APITestCase):
    def setUp(self):
        self.drone1 = Drone.objects.create(
            serial_number='UYT-095',
            model='HEAVYWEIGHT',
            weight_limit=400,
            battery_capacity=80.0,
            state='IDLE',
        )
        self.drone2 = Drone.objects.create(
            serial_number='UYT-096',
            model='MIDDLEWEIGHT',
            weight_limit=400,
            battery_capacity=20.0,  # Battery below 25%, should not be included
            state='IDLE',
        )
        self.drone3 =Drone.objects.create(
            serial_number='TEST-004',
            model='CRUISERWEIGHT',
            weight_limit=400,
            battery_capacity=30.0,
            state='LOADED'  # State not 'IDLE', should not be included
        )
        
    def tearDown(self):
        Drone.objects.all().delete()
        
    def test_get_available_drones(self):
        url = reverse('available_drones_for_loading')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['available_drones']), 1)
        
        """Verify the structure and content of each drone in the response"""
        for drone_data in response.data['available_drones']:
            self.assertIn('id', drone_data)
            self.assertIn('serial_number', drone_data)
            self.assertIn('model', drone_data)
            self.assertIn('weight_limit', drone_data)
            self.assertIn('battery_capacity', drone_data)
            self.assertIn('state', drone_data)
            self.assertGreaterEqual(drone_data['battery_capacity'], 25)
            self.assertEqual(drone_data['state'], 'IDLE')
             
              
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
        self.assertEqual(response.data['id'], self.drone.id)
        self.assertEqual(response.data['drone_serial_number'], self.drone.serial_number)
        self.assertEqual(response.data['battery_level'], self.drone.battery_capacity)

    def test_check_drone_battery_level_not_found(self):
        """Test case where drone does not exist"""
        invalid_url = reverse('check_drone_battery', kwargs={'id': self.drone.id + 1})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'Drone not found')
