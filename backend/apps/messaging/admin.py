from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at', 'updated_at', 'is_deleted')
    list_filter = ('conversation', 'sender', 'is_deleted')
    search_fields = ('id', 'text')