from rest_framework import serializers
from .models import ChatSession, Message

class MessageSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="sender")
    content = serializers.CharField(source="text")

    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'session_id', 'created_at', 'last_updated']

