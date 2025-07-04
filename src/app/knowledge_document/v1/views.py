from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import GenericViewSet

from app.common.pagination import CursorPagination
from app.knowledge_document.models import KnowledgeDocument
from app.knowledge_document.v1.filters import KnowledgeDocumentFilter
from app.knowledge_document.v1.permissions import KnowledgeDocumentPermission
from app.knowledge_document.v1.serializers import KnowledgeDocumentSerializer


@extend_schema_view(
    list=extend_schema(summary="KnowledgeDocument 목록 조회"),
    create=extend_schema(summary="KnowledgeDocument 등록"),
    retrieve=extend_schema(summary="KnowledgeDocument 상세 조회"),
    update=extend_schema(summary="KnowledgeDocument 수정"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="KnowledgeDocument 삭제"),
)
class KnowledgeDocumentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = KnowledgeDocument.objects.all()
    serializer_class = KnowledgeDocumentSerializer
    permission_classes = [KnowledgeDocumentPermission]
    pagination_class = CursorPagination
    filterset_class = KnowledgeDocumentFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    # 특정 action에 다른 Filter를 설정해야하는 경우 사용
    def get_filterset_class(self):
        return getattr(self, "filterset_class", None)

    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed("patch")
