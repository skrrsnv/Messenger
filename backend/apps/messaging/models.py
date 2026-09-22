from django.db import models
from django.contrib.auth import get_user_model
from apps.conversations.models import Conversation

User = get_user_model()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message {self.pk} by Sender {self.sender} in Conversation {self.conversation}"
