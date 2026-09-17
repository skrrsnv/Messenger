from rest_framework import serializers
from .models import Conversation, ConversationMember

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
        

class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = [
            'id',
            'conversation',
            'user',
            'role',
            'joined_at',
        ]