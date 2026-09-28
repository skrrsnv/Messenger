from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'text',
            'created_at',
            'updated_at',
            'is_deleted'
        ]
        read_only_fields = [
            "id",
            "conversation",
            "sender",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        
        def validate(self, attrs):
            if self.instance and self.instance.is_deleted:
                raise serializers.ValidationError("Deleted messages cannot be edited.")

            return attrs

        def to_representation(self, instance):
            data = super().to_representation(instance)

            if instance.is_deleted:
                data["text"] = ""

            return data