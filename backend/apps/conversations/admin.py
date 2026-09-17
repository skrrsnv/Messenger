from django.contrib import admin
from .models import Conversation, ConversationMember

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'title', 'created_at', 'updated_at')
    list_filter = ('type', )
    search_fields = ('id', 'title', )
    
@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'user', 'role', 'joined_at')
    list_filter = ('conversation', 'user')
    search_fields = ('id', 'conversation')