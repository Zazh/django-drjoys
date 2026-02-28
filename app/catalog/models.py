from decimal import InvalidOperation, Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .utils import optimize_image_field


# ─── Категория ───

class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Обложка', upload_to='categories/', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    meta_title = models.CharField('META Title', max_length=200, blank=True)
    meta_description = models.TextField('META Description', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        if self.image:
            if self.pk:
                try:
                    old = Category.objects.get(pk=self.pk)
                    image_changed = old.image.name != self.image.name
                except Category.DoesNotExist:
                    image_changed = True
            else:
                image_changed = True
            if image_changed:
                result = optimize_image_field(self.image, max_width=600, quality=80)
                if result:
                    self.image = result
        super().save(*args, **kwargs)


# ─── Товар ───

class Product(models.Model):

    class Badge(models.TextChoices):
        BESTSELLER = 'bestseller', 'Хит продаж'
        NEW = 'new', 'Новинка'
        SALE = 'sale', 'Скидка'

    name = models.CharField('Название', max_length=300)
    slug = models.SlugField('Slug', max_length=300, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категория',
    )

    description = models.TextField('Описание', blank=True)

    badge = models.CharField(
        'Бейдж', max_length=20, choices=Badge.choices, blank=True,
    )
    is_active = models.BooleanField('Активен', default=True)

    # Zoom (одна картинка, скролл-эффект)
    zoom_image = models.ImageField(
        'Zoom изображение', upload_to='products/zoom/', blank=True,
    )
    zoom_rotation_angle = models.IntegerField(
        'Угол поворота (GSAP)', default=15,
        help_text='Градус поворота для zoom-эффекта при скролле',
    )

    meta_title = models.CharField('META Title', max_length=200, blank=True)
    meta_description = models.TextField('META Description', blank=True)

    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug,
        })

    def save(self, *args, **kwargs):
        if self.zoom_image:
            if self.pk:
                try:
                    old = Product.objects.get(pk=self.pk)
                    image_changed = old.zoom_image.name != self.zoom_image.name
                except Product.DoesNotExist:
                    image_changed = True
            else:
                image_changed = True
            if image_changed:
                result = optimize_image_field(self.zoom_image, max_width=1400, quality=85)
                if result:
                    self.zoom_image = result
        super().save(*args, **kwargs)


# ─── Размеры (варианты) ───

class ProductSize(models.Model):
    """Размер товара с артикулом и ценой."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='sizes', verbose_name='Товар',
    )
    name = models.CharField('Размер', max_length=50,
        help_text='Например: M, L, XL, 3 шт, 12 шт',
    )
    sku = models.CharField('Артикул', max_length=50, unique=True)

    # Цены KZT (основная валюта)
    price = models.DecimalField('Цена (₸)', max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        'Старая цена (₸)', max_digits=10, decimal_places=2, blank=True, null=True,
    )
    # Цены RUB
    price_rub = models.DecimalField(
        'Цена (₽)', max_digits=10, decimal_places=2, blank=True, null=True,
    )
    old_price_rub = models.DecimalField(
        'Старая цена (₽)', max_digits=10, decimal_places=2, blank=True, null=True,
    )

    in_stock = models.BooleanField('В наличии', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f'{self.product.name} — {self.name}'

    @property
    def has_discount(self):
        return self.old_price is not None and self.old_price > self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            return round((1 - self.price / self.old_price) * 100)
        return 0


# ─── Характеристики ───

class UnitOfMeasure(models.Model):
    """Единица измерения с типом данных значения."""

    class DataType(models.TextChoices):
        TEXT = 'text', 'Строка'
        INTEGER = 'integer', 'Целое число'
        DECIMAL = 'decimal', 'Десятичное число'

    name = models.CharField('Название', max_length=100)
    abbr = models.CharField('Сокращение', max_length=20)
    data_type = models.CharField(
        'Тип данных', max_length=10,
        choices=DataType.choices, default=DataType.TEXT,
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.abbr})'


class Characteristic(models.Model):
    """Определение характеристики (Толщина, Материал и т.д.)."""
    name = models.CharField('Название', max_length=200)
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Единица измерения',
        help_text='Если не указана — значение свободный текст',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
        ordering = ['order', 'name']

    def __str__(self):
        if self.unit:
            return f'{self.name} ({self.unit.abbr})'
        return self.name


class ProductCharacteristic(models.Model):
    """Значение характеристики для конкретного товара."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='characteristics', verbose_name='Товар',
    )
    characteristic = models.ForeignKey(
        Characteristic, on_delete=models.CASCADE,
        verbose_name='Характеристика',
    )
    value = models.CharField('Значение', max_length=500)

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товара'
        unique_together = ['product', 'characteristic']
        ordering = ['characteristic__order']

    def __str__(self):
        return f'{self.characteristic.name}: {self.value}'

    def clean(self):
        """Валидация значения по типу данных юнита."""
        unit = self.characteristic.unit if self.characteristic_id else None
        if not unit:
            return  # текст — любое значение допустимо

        if unit.data_type == UnitOfMeasure.DataType.INTEGER:
            try:
                int(self.value)
            except (ValueError, TypeError):
                raise ValidationError(
                    {'value': f'Для "{self.characteristic.name}" нужно целое число'}
                )
        elif unit.data_type == UnitOfMeasure.DataType.DECIMAL:
            try:
                Decimal(self.value)
            except (InvalidOperation, ValueError, TypeError):
                raise ValidationError(
                    {'value': f'Для "{self.characteristic.name}" нужно число'}
                )


# ─── Изображения товара ───

class ProductMainImage(models.Model):
    """Основные фото товара. Одно помечается как обложка (is_cover)."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='main_images', verbose_name='Товар',
    )
    image = models.ImageField('Изображение', upload_to='products/main/')
    thumbnail = models.ImageField(
        'Миниатюра', upload_to='products/thumbs/',
        blank=True, editable=False,
    )
    alt_text = models.CharField('Alt текст', max_length=300, blank=True)
    is_cover = models.BooleanField('Обложка', default=False,
        help_text='Главная картинка товара (одна на товар)',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Основное фото'
        verbose_name_plural = 'Основные фото'
        ordering = ['-is_cover', 'order']

    def __str__(self):
        cover = ' [обложка]' if self.is_cover else ''
        return f'{self.product.name} — основное{cover}'

    def save(self, *args, **kwargs):
        if self.image:
            if self.pk:
                try:
                    old = ProductMainImage.objects.get(pk=self.pk)
                    image_changed = old.image.name != self.image.name
                except ProductMainImage.DoesNotExist:
                    image_changed = True
            else:
                image_changed = True
            if image_changed:
                # Оптимизация основного изображения (800px)
                result = optimize_image_field(self.image, max_width=800, quality=85)
                if result:
                    self.image = result
                # Генерация миниатюры для каталога (600px)
                thumb = optimize_image_field(self.image, max_width=600, quality=80)
                if thumb:
                    self.thumbnail = thumb
        super().save(*args, **kwargs)


class ProductPackageImage(models.Model):
    """Фото упаковки (слайдер)."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='package_images', verbose_name='Товар',
    )
    image = models.ImageField('Изображение', upload_to='products/package/')
    alt_text = models.CharField('Alt текст', max_length=300, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото упаковки'
        verbose_name_plural = 'Фото упаковки'
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — упаковка'

    def save(self, *args, **kwargs):
        if self.image:
            if self.pk:
                try:
                    old = ProductPackageImage.objects.get(pk=self.pk)
                    image_changed = old.image.name != self.image.name
                except ProductPackageImage.DoesNotExist:
                    image_changed = True
            else:
                image_changed = True
            if image_changed:
                result = optimize_image_field(self.image, max_width=800, quality=82)
                if result:
                    self.image = result
        super().save(*args, **kwargs)


class ProductIndividualImage(models.Model):
    """Фото индивидуальной упаковки (слайдер)."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='individual_images', verbose_name='Товар',
    )
    image = models.ImageField('Изображение', upload_to='products/individual/')
    alt_text = models.CharField('Alt текст', max_length=300, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото индивидуальной упаковки'
        verbose_name_plural = 'Фото индивидуальной упаковки'
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — индивидуальная'

    def save(self, *args, **kwargs):
        if self.image:
            if self.pk:
                try:
                    old = ProductIndividualImage.objects.get(pk=self.pk)
                    image_changed = old.image.name != self.image.name
                except ProductIndividualImage.DoesNotExist:
                    image_changed = True
            else:
                image_changed = True
            if image_changed:
                result = optimize_image_field(self.image, max_width=800, quality=82)
                if result:
                    self.image = result
        super().save(*args, **kwargs)


# ─── FAQ ───

class FAQ(models.Model):
    question = models.CharField('Вопрос', max_length=500)
    answer = models.TextField('Ответ')
    is_active = models.BooleanField('Активен', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['order']

    def __str__(self):
        return self.question


# ─── Настройки сайта ───

class SiteSettings(models.Model):
    """Singleton: глобальные настройки сайта (всегда pk=1)."""
    placeholder_image = models.ImageField(
        'Плейсхолдер товара', upload_to='site/', blank=True,
        help_text='Заглушка для товаров без фото. Если не задано — SVG по умолчанию.',
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        self.pk = 1
        if self.placeholder_image:
            if self._placeholder_image_changed():
                result = optimize_image_field(self.placeholder_image, max_width=800, quality=82)
                if result:
                    self.placeholder_image = result
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def _placeholder_image_changed(self):
        try:
            old = SiteSettings.objects.get(pk=self.pk)
            return old.placeholder_image.name != self.placeholder_image.name
        except SiteSettings.DoesNotExist:
            return True

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
