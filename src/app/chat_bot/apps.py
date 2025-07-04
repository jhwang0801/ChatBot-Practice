from django.apps import AppConfig


class ChatBotConfig(AppConfig):
    name = "app.chat_bot"

    def ready(self):
        import app.chat_bot.signals
