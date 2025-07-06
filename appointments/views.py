from django.shortcuts import render, redirect
from .models import Service, Booking
from users.models import User, UserLevel
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from datetime import date
from utils.whatsapp import send_whatsapp_message

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

        booking = Booking.objects.create(
            user=user,
            service=service,
            staff=staff,
            date=request.POST['date'],
            time=request.POST['time'],
            status='pending',
        )
        send_whatsapp_message(
            to=user.phone,
            message=f"Hi {user.first_name}, your appointment for {service.name} is booked on {booking.date} at {booking.time}. We'll confirm it shortly!"
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
    end_time = datetime.combine(date, datetime.strptime('23:00', '%H:%M').time())

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


def staff_dashboard(request):
    user_id = request.session.get("user_id")
    user_role = request.session.get("role")

    if not user_id or user_role != "staff":
        return redirect("login")

    user = User.objects.get(id=user_id)
    bookings = Booking.objects.filter(staff_id=user_id)

    status = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if status in ["pending", "confirmed", "cancelled"]:
        bookings = bookings.filter(status=status)

    if start_date:
        bookings = bookings.filter(date__gte=start_date)
    else:
        bookings = bookings.filter(date__gte=date.today())

    if end_date:
        bookings = bookings.filter(date__lte=end_date)

    bookings = bookings.order_by("date", "time")

    context = {
        "user": user,
        "bookings": bookings,
        "selected_status": status,
        "selected_date": start_date,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "appointments/staff_dashboard.html", context)

def admin_dashboard(request):
    user_id = request.session.get("user_id")
    user_role = request.session.get("role")

    if not user_id or user_role != "admin":
        return redirect("login")

    user = User.objects.get(id=user_id)
    today = date.today()
    bookings = Booking.objects.select_related("user", "staff", "service").filter(date__gte=today)

    status = request.GET.get("status")
    staff_id = request.GET.get("staff")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if status in ["pending", "confirmed", "cancelled"]:
        bookings = bookings.filter(status=status)
    if staff_id and staff_id.isdigit():
        bookings = bookings.filter(staff_id=int(staff_id))
    if start_date:
        bookings = bookings.filter(date__gte=start_date)
    if end_date:
        bookings = bookings.filter(date__lte=end_date)

    bookings = bookings.order_by("date", "time")

    context = {
        "user": user,
        "bookings": bookings,
        "selected_status": status,
        "selected_staff": int(staff_id) if staff_id and staff_id.isdigit() else None,
        "selected_start": start_date,
        "selected_end": end_date,
        "staff_members": User.objects.filter(user_level__level_name="staff")
    }
    return render(request, "appointments/admin_dashboard.html", context)

def update_booking_status(request, booking_id, action):
    user_id = request.session.get("user_id")
    user_role = request.session.get("role")

    if not user_id:
        return redirect("login")

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect("staff_dashboard" if user_role == "staff" else "admin_dashboard")

    if user_role == "staff" and booking.staff_id != user_id:
        messages.error(request, "Unauthorized access to booking.")
        return redirect("book_appointment")

    if action == "confirm":
        booking.status = "confirmed"
        booking.save()
        messages.success(request, "Booking confirmed.")
    elif action == "cancel":
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Booking cancelled.")
    else:
        messages.error(request, "Invalid action.")

    return redirect("admin_dashboard" if user_role == "admin" else "staff_dashboard")