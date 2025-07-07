from django.http import JsonResponse
from .models import Notification
from users.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def unread_notifications(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid user'}, status=401)

    unread = Notification.objects.filter(recipient=user, is_read=False).values('id', 'message', 'created_at')
    return JsonResponse({"notifications": list(unread)})

@csrf_exempt
@require_POST
def mark_as_read(request, notification_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        notification = Notification.objects.get(id=notification_id, recipient_id=user_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"error": "Notification not found"}, status=404)
