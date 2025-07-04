from django.contrib import admin

from .models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "created_at", "message_count")
    readonly_fields = ("session_id", "created_at")

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = "메시지 수"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "user_message_short", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("session", "user_message", "bot_response", "sources", "created_at")

    def user_message_short(self, obj):
        return obj.user_message[:50] + "..." if len(obj.user_message) > 50 else obj.user_message

    user_message_short.short_description = "사용자 메시지"
