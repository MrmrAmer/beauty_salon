from django.shortcuts import render, redirect
from .models import ChatMessage
from users.models import User
from django.contrib import messages
import random

def chat_home(request):
    if 'user_id' not in request.session:
        return redirect('/login')

    user = User.objects.get(id=request.session['user_id'])
    context = {
        'user': user,
        'messages': ChatMessage.objects.filter(user=user).order_by('-created_at')
    }
    return render(request, 'chat/chat_home.html', context)


def send_message(request):
    if 'user_id' not in request.session or request.method != 'POST':
        return redirect('/chat/')

    user = User.objects.get(id=request.session['user_id'])
    message = request.POST.get('message', '').strip()

    errors = ChatMessage.objects.basic_validator({'message': message})
    if errors:
        for e in errors.values():
            messages.error(request, e)
        return redirect('/chat/')

    response = generate_bot_response(message)

    ChatMessage.objects.create(
        user=user,
        message=message,
        response=response
    )

    return redirect('/chat/')

def generate_bot_response(message):
    msg = message.lower()
    if "book" in msg:
        return "To book an appointment, please go to the services page."
    elif "cancel" in msg:
        return "To cancel, visit your bookings page."
    return random.choice([
        "I’m here to help with appointments and orders!",
        "You can ask me to book or cancel your visit.",
        "Visit the services page to get started.",
    ])