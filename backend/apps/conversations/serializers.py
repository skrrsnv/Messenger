from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            'type',
            'title',
            'avatar',
            'created_at',
            'updated_at',    
        ]