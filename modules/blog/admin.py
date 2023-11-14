from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin
from .models import Article, Category, Comment, ViewCount


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели категорий
    """
    list_display = ('tree_actions', 'indented_title', 'id', 'title', 'slug')
    list_display_links = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'slug', 'parent')}),
        ('Описание', {'fields': ('description',)})
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Админ-панель модели статей
    """
    list_display = ('title', 'author', 'time_create',)


@admin.register(Comment)
class CommentAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели комментариев
    """
    list_display = ('tree_actions', 'indented_title', 'article', 'author', 'time_create', 'status')
    mptt_level_indent = 2
    list_display_links = ('article',)
    list_filter = ('time_create', 'time_update', 'author')
    list_editable = ('status',)


@admin.register(ViewCount)
class ViewCountAdmin(admin.ModelAdmin):
    pass
