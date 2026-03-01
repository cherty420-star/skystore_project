from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Админка для блоговых записей"""
    list_display = ('id', 'title', 'created_at', 'is_published', 'views_count')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'preview')
        }),
        ('Статус', {
            'fields': ('is_published', 'views_count', 'created_at')
        }),
    )