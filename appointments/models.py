from django.db import models
from users.models import User

DURATION_CHOICES = [
    ("30 minutes", "30 minutes"),
    ("1 hour", "1 hour"),
    ("1.5 hours", "1.5 hours"),
]

class Service(models.Model):
    name = models.CharField(max_length=45)
    description = models.TextField()
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.IntegerField()
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def duration_in_minutes(self):
        mapping = {
            "30 minutes": 30,
            "1 hour": 60,
            "1.5 hours": 90,
        }
        return mapping.get(self.duration, 30)


class BookingManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        if not post_data.get('date'):
            errors['date'] = "Date is required."

        if not post_data.get('time'):
            errors['time'] = "Time is required."

        return errors
    

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
)

class Booking(models.Model):
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="booked_services")
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="staff_bookings")
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookingManager()

    def __str__(self):
        return f"Booking #{self.id} on {self.date} at {self.time}"