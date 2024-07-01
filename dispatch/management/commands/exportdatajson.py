import os
import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from dispatch.models import Drone, Medication, DroneBatteryAudit

class Command(BaseCommand):
    help = 'Export data from models to JSON files'

    def handle(self, *args, **options):
        try:
            # Export Drone data
            drones_data = serialize('json', Drone.objects.all())
            self.write_to_file('drones.json', drones_data)

            # Export Medication data
            medications_data = serialize('json', Medication.objects.all())
            self.write_to_file('medications.json', medications_data)

            # Export DroneBatteryAudit data
            audits_data = serialize('json', DroneBatteryAudit.objects.all())
            self.write_to_file('drone_battery_audits.json', audits_data)

            self.stdout.write(self.style.SUCCESS('Successfully exported data to JSON files'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to export data: {str(e)}'))

    def write_to_file(self, filename, data):
        file_path = os.path.join('data_exports', filename)  
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(data)
