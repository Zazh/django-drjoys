from django.db import models
from django.urls import reverse


class Page(models.Model):
    """Статичная страница (about, partners, contacts и т.д.)."""
    title = models.CharField('Заголовок', max_length=300)
    slug = models.SlugField('Slug', max_length=300, unique=True,
        help_text='URL страницы: about, partners, contacts',
    )
    body = models.TextField('Контент', help_text='HTML-контент страницы')
    meta_title = models.CharField('META Title', max_length=200, blank=True)
    meta_description = models.TextField('META Description', blank=True)
    og_image = models.ImageField('OG Image', upload_to='pages/og/', blank=True)
    is_published = models.BooleanField('Опубликована', default=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})


class BlogCategory(models.Model):
    """Категория блога."""
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Категория блога'
        verbose_name_plural = 'Категории блога'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Статья блога."""
    title = models.CharField('Заголовок', max_length=300)
    slug = models.SlugField('Slug', max_length=300, unique=True)
    excerpt = models.TextField('Краткое описание', blank=True,
        help_text='Текст для карточки в списке блога',
    )
    body = models.TextField('Контент', help_text='HTML-контент статьи')
    cover_image = models.ImageField('Обложка', upload_to='blog/covers/', blank=True)
    author = models.CharField('Автор', max_length=200, blank=True)
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts', verbose_name='Категория',
    )
    meta_title = models.CharField('META Title', max_length=200, blank=True)
    meta_description = models.TextField('META Description', blank=True)
    is_published = models.BooleanField('Опубликована', default=True)
    published_at = models.DateTimeField('Дата публикации')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-published_at', 'is_published']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:blog_detail', kwargs={'slug': self.slug})
