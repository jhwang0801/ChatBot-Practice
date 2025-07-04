import uuid

from django.db import models


class ChatSession(models.Model):
    session_id = models.UUIDField("세션 ID", default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "채팅 세션"
        verbose_name_plural = "채팅 세션들"
        ordering = ["-created_at"]

    def __str__(self):
        return f"세션 {self.session_id}"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")

    user_message = models.TextField("사용자 메시지")
    bot_response = models.TextField("봇 응답")
    sources = models.JSONField("참조 문서들", default=list, blank=True)

    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지들"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.session.session_id} - {self.user_message[:30]}..."
