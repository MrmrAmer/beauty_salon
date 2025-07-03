from django.shortcuts import render
from appointments.models import Service

def services(request):
    context = {
        'services': Service.objects.all(),
    }
    return render(request, 'services/services.html', context)