from django.shortcuts import render, redirect
from .models import Service, Booking
from users.models import User, UserLevel
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from datetime import date

def book_appointment(request, service_id=None):
    if 'user_id' not in request.session:
        next_url = f"/appointments/book/{service_id}/" if service_id else "/appointments/"
        return redirect(f"/login?next={next_url}")

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
        'today': date.today(),
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

def get_available_slots(request):
    date_str = request.GET.get('date')
    staff_id = request.GET.get('staff')
    service_id = request.GET.get('service')

    if not (date_str and staff_id and service_id):
        return JsonResponse({'error': 'Missing data'}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        service = Service.objects.get(id=service_id)
    except (ValueError, Service.DoesNotExist):
        return JsonResponse({'error': 'Invalid date or service'}, status=400)

    service_duration = service.duration_in_minutes()
    step = timedelta(minutes=service_duration)

    start_time = datetime.combine(date, datetime.strptime('09:00', '%H:%M').time())
    end_time = datetime.combine(date, datetime.strptime('17:00', '%H:%M').time())

    existing_bookings = Booking.objects.filter(
        staff_id=staff_id,
        date=date
    )

    booked_ranges = []
    for booking in existing_bookings:
        booking_service = booking.service
        booking_start = datetime.combine(date, booking.time)
        booking_end = booking_start + timedelta(minutes=booking_service.duration_in_minutes())
        booked_ranges.append((booking_start.time(), booking_end.time()))

    slots = []
    while start_time + step <= end_time:
        slot_start = start_time.time()
        slot_end = (start_time + step).time()

        if not any(start < slot_end and end > slot_start for start, end in booked_ranges):
            slots.append(slot_start.strftime('%H:%M'))

        start_time += timedelta(minutes=15)

    return JsonResponse({'slots': slots})