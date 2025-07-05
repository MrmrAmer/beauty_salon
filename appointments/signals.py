from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Booking
from utils.whatsapp import send_whatsapp_message

# Save original status before change
@receiver(pre_save, sender=Booking)
def notify_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object — let post_save handle it

    try:
        old_instance = Booking.objects.get(pk=instance.pk)
    except Booking.DoesNotExist:
        return

    if old_instance.status != instance.status:
        user = instance.user
        phone = user.phone

        if not phone:
            return

        if phone.startswith("00"):
            phone = "+" + phone[2:]

        if instance.status == "confirmed":
            msg = (
                f"Hi {user.first_name}, your appointment on {instance.date} at {instance.time} "
                f"has been confirmed. We look forward to seeing you!"
            )
            send_whatsapp_message(phone, msg)

        elif instance.status == "cancelled":
            msg = (
                f"Hi {user.first_name}, we're sorry to inform you that your appointment on "
                f"{instance.date} at {instance.time} has been cancelled. Please contact us to reschedule."
            )
            send_whatsapp_message(phone, msg)
