from datetime import datetime, timedelta
from django.utils import timezone
from appointments.models import Booking
from utils.whatsapp import send_whatsapp_message
from django.db import transaction

def send_upcoming_reminders():
    tz = timezone.get_current_timezone()
    now = timezone.localtime(timezone.now(), tz)
    one_hour_later = now + timedelta(hours=1)

    print(f"[Reminder Task] Now (Asia/Jerusalem): {now}")
    print(f"[Reminder Task] Looking for bookings between {now} and {one_hour_later}")

    # Only get bookings not yet reminded
    qs = Booking.objects.select_for_update().filter(status="confirmed", reminder_sent=False)
    
    sent = 0
    with transaction.atomic():
        for booking in qs:
            dt = datetime.combine(booking.date, booking.time)
            dt = timezone.make_aware(dt, tz) if timezone.is_naive(dt) else dt

            if now <= dt <= one_hour_later:
                # Double-check again inside transaction to avoid race condition
                if not booking.reminder_sent:
                    message = (
                        f"Reminder: You have an appointment for {booking.service.name} "
                        f"at {booking.time.strftime('%H:%M')} on {booking.date.strftime('%Y-%m-%d')}."
                    )
                    send_whatsapp_message(booking.user.phone, message)
                    booking.reminder_sent = True
                    booking.save(update_fields=['reminder_sent'])
                    sent += 1

    print(f"[Reminder Task] Sent {sent} WhatsApp reminder(s).")
