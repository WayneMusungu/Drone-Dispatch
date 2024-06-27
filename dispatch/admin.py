from django.contrib import admin
from .models import Drone, Medication

# Register your models here.

@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model', 'weight_limit', 'battery_capacity', 'state')
    
    
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'code', 'image', 'drone')
    list_filter = ('drone',)
    search_fields = ('name', 'code')