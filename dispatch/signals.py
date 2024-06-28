from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from dispatch.models import DroneBatteryAudit
from dispatch.tasks import delete_expired_audit_logs

@receiver(post_save, sender=DroneBatteryAudit)
@receiver(post_delete, sender=DroneBatteryAudit)
def schedule_delete_expired_logs(sender, instance, **kwargs):
    # Schedule the task to delete expired logs
    delete_expired_audit_logs.apply_async()
