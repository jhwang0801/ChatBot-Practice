from django.urls import include, path

urlpatterns = [
    # path("v1/", include("app.user.v1.urls")),
    # path("v1/", include("app.knowledge_document.v1.urls")),
    path("v1/", include("app.chat_bot.v1.urls")),
]
