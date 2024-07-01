from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from dispatch.models import Drone, Medication, DroneBatteryAudit
from dispatch.tasks import perform_check_drone_battery

class DroneMedicationModelTest(TestCase):

    def setUp(self):
        self.drone = Drone.objects.create(
            serial_number='TEST-001',
            model='Model A',
            weight_limit=500,
            battery_capacity=80.0,
            state='IDLE'
        )
        self.medication = Medication.objects.create(
            name='Med-001',
            weight=50.0,
            code='MED001',
            image='media/image.jpg',
            drone=self.drone
        )
        
    def tearDown(self):
        Drone.objects.all().delete()
        Medication.objects.all().delete()

    def test_drone_creation(self):
        drone = Drone.objects.get(serial_number='TEST-001')
        self.assertEqual(drone.model, 'Model A')
        self.assertEqual(drone.weight_limit, 500)
        self.assertEqual(drone.battery_capacity, 80.0)
        self.assertEqual(drone.state, 'IDLE')

    def test_medication_creation(self):
        medication = Medication.objects.get(code='MED001')
        self.assertEqual(medication.name, 'Med-001')
        self.assertEqual(medication.weight, 50.0)
        self.assertEqual(medication.drone, self.drone)

    def test_invalid_medication_name(self):
        with self.assertRaises(ValidationError):
            invalid_medication = Medication(
                name='Invalid Name!',
                weight=50.0,
                code='INVALID001',
                image='media/image.jpg',
                drone=self.drone
            )
            invalid_medication.clean()

    def test_invalid_medication_code(self):
        with self.assertRaises(ValidationError):
            invalid_medication = Medication(
                name='ValidName',
                weight=50.0,
                code='invalid_code',
                image='mediaimage.jpg',
                drone=self.drone
            )
            invalid_medication.clean()

class DroneBatteryAuditPeriodicTaskTest(TestCase):

    def setUp(self):
        self.drone1 = Drone.objects.create(
            serial_number='TEST-003',
            model='Model A',
            weight_limit=500,
            battery_capacity=80.0,
            state='IDLE'
        )
        self.drone2 = Drone.objects.create(
            serial_number='TEST-004',
            model='Model B',
            weight_limit=400,
            battery_capacity=60.0,
            state='IDLE'
        )
        
    def tearDown(self):
        Drone.objects.all().delete()
        DroneBatteryAudit.objects.all().delete()

    @patch('dispatch.tasks.logger')
    def test_perform_check_drone_battery(self, mock_logger):
        perform_check_drone_battery()

        audits = DroneBatteryAudit.objects.all()
        self.assertEqual(audits.count(), 2)

        audit1 = DroneBatteryAudit.objects.get(drone=self.drone1)
        self.assertEqual(audit1.battery_level, 80.0)
        self.assertEqual(audit1.task_name, 'dispatch.tasks.perform_check_drone_battery')

        audit2 = DroneBatteryAudit.objects.get(drone=self.drone2)
        self.assertEqual(audit2.battery_level, 60.0)
        self.assertEqual(audit2.task_name, 'dispatch.tasks.perform_check_drone_battery')

        mock_logger.info.assert_called()