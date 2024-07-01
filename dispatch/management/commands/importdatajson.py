import os
import json
from django.core.management.base import BaseCommand
from dispatch.models import Drone, Medication

class Command(BaseCommand):
    help = 'Import data from JSON files to database'

    def handle(self, *args, **options):
        try:
            # Import Drones from JSON
            file_path_drones = 'data_exports/drones.json'  
            with open(file_path_drones, 'r') as file:
                drones_data = json.load(file)
                for drone_obj in drones_data:
                    fields = drone_obj['fields']
                    drone = Drone(
                        serial_number=fields['serial_number'],
                        model=fields['model'],
                        weight_limit=fields['weight_limit'],
                        battery_capacity=fields['battery_capacity'],
                        state=fields['state']
                    )
                    drone.save()

            # Import Medications from JSON
            file_path_medications = 'data_exports/medications.json'  
            with open(file_path_medications, 'r') as file:
                medications_data = json.load(file)
                for medication_obj in medications_data:
                    fields = medication_obj['fields']
                    medication = Medication(
                        name=fields['name'],
                        weight=fields['weight'],
                        code=fields['code'],
                        image=fields['image'],  
                        drone_id=fields['drone']  
                    )
                    medication.save()

            self.stdout.write(self.style.SUCCESS('Successfully imported data to database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import data: {str(e)}'))
