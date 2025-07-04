# =================== Django 관리 명령어 ===================

# management/commands/embed_content.py
from django.core.management.base import BaseCommand

from app.chat_bot.rag_service import CompanyChatbotService


class Command(BaseCommand):
    help = "모든 컨텐츠를 크로마에 임베딩합니다"

    def handle(self, *args, **options):
        service = CompanyChatbotService()
        service.embed_all_content()
        self.stdout.write(self.style.SUCCESS("✅ 모든 컨텐츠 임베딩이 완료되었습니다!"))
