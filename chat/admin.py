from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'response', 'created_at')
    search_fields = ('user__first_name', 'message', 'response')
    list_filter = ('created_at',)