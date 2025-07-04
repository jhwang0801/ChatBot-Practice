from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.knowledge_document.v1.views import KnowledgeDocumentViewSet

router = DefaultRouter()
router.register("knowledge_document", KnowledgeDocumentViewSet, basename="knowledge_document")

urlpatterns = [
    path("", include(router.urls)),
]
