from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_appointment, name='book_appointment'),
    path('book/<int:service_id>/', views.book_appointment, name='book'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/get-slots/', views.get_available_slots, name='get_available_slots'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update/<int:booking_id>/<str:action>/', views.update_booking_status, name='update_booking_status'),
]