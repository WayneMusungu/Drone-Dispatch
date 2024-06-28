from celery import shared_task
from django.utils import timezone
from .models import Drone, DroneBatteryAudit
import logging

logger = logging.getLogger(__name__)

@shared_task(name='dispatch.tasks.delete_expired_audit_logs')
def delete_expired_audit_logs():
    expiry_threshold = timezone.now() - timezone.timedelta(minutes=4)  # Expire logs older than 4 minutes
    expired_logs = DroneBatteryAudit.objects.filter(timestamp__lte=expiry_threshold)
    count = expired_logs.count()
    expired_logs.delete()
    logger.info(f"Deleted {count} expired audit logs.")

@shared_task(name='dispatch.tasks.perform_check_drone_battery')
def perform_check_drone_battery():
    drones = Drone.objects.all()
    current_task_name = perform_check_drone_battery.name  # Get current task name
    for drone in drones:
        logger.info(f'Drone {drone.serial_number} battery level: {drone.battery_capacity}')
        # Save battery audit log including task name
        audit_log = DroneBatteryAudit.objects.create(
            drone=drone,
            battery_level=drone.battery_capacity,
            task_name=current_task_name,
            expiry_duration_minutes=5  # Set expiry duration in minutes
        )
        logger.info(f"Saved audit log for Task '{current_task_name}' - {audit_log}")
