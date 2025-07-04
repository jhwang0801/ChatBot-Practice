from django.apps import AppConfig


class KnowledgeDocumentConfig(AppConfig):
    name = "app.knowledge_document"

    def ready(self):
        import app.knowledge_document.signals
