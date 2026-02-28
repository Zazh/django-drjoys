from modeltranslation.translator import register, TranslationOptions

from .models import Page, BlogCategory, BlogPost


@register(Page)
class PageTO(TranslationOptions):
    fields = ('title', 'body', 'meta_title', 'meta_description')


@register(BlogCategory)
class BlogCategoryTO(TranslationOptions):
    fields = ('name',)


@register(BlogPost)
class BlogPostTO(TranslationOptions):
    fields = ('title', 'excerpt', 'body', 'meta_title', 'meta_description')
