from django.shortcuts import render, redirect
from .models import Service, Booking
from users.models import User, UserLevel
from django.contrib import messages

def book_appointment(request, service_id=None):
    if 'user_id' not in request.session:
        return redirect(f"/login?next=/appointments/book/{service_id or ''}")

    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        errors = Booking.objects.basic_validator(request.POST)
        if errors:
            for key, msg in errors.items():
                messages.error(request, msg)
            return redirect('/appointments/book/')

        service = Service.objects.get(id=request.POST['service_id'])
        staff = User.objects.get(id=request.POST['staff_id'])

        Booking.objects.create(
            user=user,
            service=service,
            staff=staff,
            date=request.POST['date'],
            time=request.POST['time'],
            status='pending',
        )
        messages.success(request, "Appointment booked successfully.")
        return redirect('/appointments/my_bookings/')

    staff_level = UserLevel.objects.get(level_name__iexact="staff")
    staff_members = User.objects.filter(user_level=staff_level)
    selected_service = Service.objects.get(id=service_id) if service_id else None

    context = {
        'user': user,
        'services': Service.objects.all(),
        'staff_members': staff_members,
        'selected_service': selected_service,
    }
    return render(request, 'appointments/book_appointment.html', context)

def my_bookings(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    user = User.objects.get(id=request.session['user_id'])
    context = {
        'user': user,
        'bookings': Booking.objects.filter(user=user).order_by('-date', '-time')
    }
    return render(request, 'appointments/my_bookings.html', context)


def cancel_booking(request, booking_id):
    if 'user_id' not in request.session:
        return redirect('/login')

    booking = Booking.objects.get(id=booking_id)
    if booking.user.id == request.session['user_id']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled.")
    return redirect('/appointments/my_bookings/')