from django.db import models

class Conversation(models.Model):
    
    class TypeChoices(models.TextChoices):
        PRIVATE = 'private', 'Private'
        GROUP = 'group', 'Group'

    type = models.CharField(max_length=10, choices=TypeChoices.choices)
    title = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Conversation {self.pk}"