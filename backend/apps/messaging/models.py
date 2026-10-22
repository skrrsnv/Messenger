from django.db import models
from django.contrib.auth import get_user_model
from apps.conversations.models import Conversation

User = get_user_model()

class Message(models.Model):
    
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_READ = "read"

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_READ, "Read"),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="messages")
    text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT, db_index=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message {self.pk} by Sender {self.sender} in Conversation {self.conversation}"


class MessageRead(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_reads")
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_message_read",
            ),
        ]
    
    def __str__(self):
        return f"Message {self.message} read by User {self.user}"
    

class MessageDelivery(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_deliveries",
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_message_delivery",
            ),
        ]

    def __str__(self):
        return f"Message {self.message_id} delivered to User {self.user_id}"