from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path("unread/", views.unread_notifications, name="unread_notifications"),
    path("mark-as-read/<int:notification_id>/", views.mark_as_read, name="mark_as_read"),
]