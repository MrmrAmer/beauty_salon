from django.contrib import admin
from .models import Service, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'staff', 'service', 'date', 'time', 'status')
    search_fields = ('user__first_name', 'staff__first_name', 'status')
    list_filter = ('status', 'date')
