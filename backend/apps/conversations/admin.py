from django.contrib import admin
from .models import Conversation

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'title', 'created_at', 'updated_at')
    list_filter = ('type', )
    search_fields = ('id', 'title', )