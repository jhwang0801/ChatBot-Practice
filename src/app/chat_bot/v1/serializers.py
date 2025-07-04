from rest_framework import serializers

from app.chat_bot.models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["user_message", "bot_response", "sources", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["session_id", "created_at", "messages"]


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    session_id = serializers.UUIDField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    sources = serializers.ListField()
    response_time = serializers.FloatField()
    session_id = serializers.UUIDField()
