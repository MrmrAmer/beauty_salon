from django.db import models
from users.models import User


class ChatMessageManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        if not post_data.get('message', '').strip():
            errors['message'] = "Message cannot be empty."

        return errors


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ChatMessageManager()

    def __str__(self):
        return f"ChatMessage #{self.id} from {self.user.first_name}"