from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.chat_bot.models import ChatMessage, ChatSession
from app.chat_bot.rag_service import CompanyChatbotService
# from app.chat_bot.rag_service import get_rag_service
from app.chat_bot.v1.serializers import ChatSessionSerializer, SendMessageSerializer


class ChatBotViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def send_message(self, request):
        user_question = request.data.get("message")
        session_id = request.data.get("session_id")

        if not user_question:
            return Response({"error": "질문을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 챗봇 서비스 실행
        chatbot = CompanyChatbotService()
        result = chatbot.process_question(user_question, session_id)

        return Response(
            {
                "question": user_question,
                "answer": result["answer"],
                "related_blogs": result["related_blogs"],
                "response_time_ms": result["response_time_ms"],
                "chat_log_id": result["chat_log_id"],
            }
        )
