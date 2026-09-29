from django.contrib import admin
from .models import Message, MessageRead

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at', 'updated_at', 'is_deleted')
    list_filter = ('conversation', 'sender', 'is_deleted')
    search_fields = ('id', 'text')
    
@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    list_filter = ('user', )
    search_fields = ('id', 'message', 'user')