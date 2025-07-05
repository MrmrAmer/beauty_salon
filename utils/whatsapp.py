from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to, message):
    if to.startswith("00"):
        to = "+" + to[2:]  # Convert 00970 → +970
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=f"whatsapp:{to}"
    )
