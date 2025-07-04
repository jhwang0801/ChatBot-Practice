from django.contrib import admin

from app.knowledge_document.models import BlogPost, Category, CompanyContent, Project


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyContent)
class CompanyContentAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass
