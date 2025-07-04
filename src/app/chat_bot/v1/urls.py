from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.chat_bot.v1.views import ChatBotViewSet

router = DefaultRouter()
router.register("chat_bot", ChatBotViewSet, basename="chat_bot")

urlpatterns = [
    path("", include(router.urls)),
]
