from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Page, BlogCategory, BlogPost


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'body'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description', 'og_image'),
        }),
        ('Настройки', {
            'fields': ('is_published',),
        }),
    )


@admin.register(BlogCategory)
class BlogCategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'published_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['category']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'body'),
        }),
        ('Медиа и автор', {
            'fields': ('cover_image', 'author', 'category', 'published_at'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
        ('Настройки', {
            'fields': ('is_published',),
        }),
    )
