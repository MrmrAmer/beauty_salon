from django.shortcuts import render, redirect
from .models import User, UserLevel
from django.contrib import messages
import bcrypt

def landing_page(request):
    return render(request, 'users/landing.html')

def register(request):
    if request.method == 'POST':
        errors = User.objects.basic_validator(request.POST)
        if errors:
            for key, msg in errors.items():
                messages.error(request, msg)
            return redirect('/register')

        user_level = UserLevel.objects.get(level_name='customer')
        pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            password=pw_hash,
            user_level=user_level
        )
        request.session['user_id'] = user.id
        next_url = request.GET.get('next')
        return redirect(next_url if next_url else '/dashboard')
    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
            if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
                request.session['user_id'] = user.id
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else '/dashboard')
            else:
                messages.error(request, "Incorrect password")
        except:
            messages.error(request, "Email not found")
        return redirect('/login')
    return render(request, 'users/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('/')

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    context = {
        'user': User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'users/dashboard.html', context)

def contact(request):
    return render(request, 'users/contact.html')