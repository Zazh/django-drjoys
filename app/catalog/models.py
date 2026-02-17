from django.db import models
from django.urls import reverse


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


class Characteristic(models.Model):
    """Определение атрибута (PIM-стиль)."""

    class ValueType(models.TextChoices):
        TEXT = 'text', 'Текст'
        NUMBER = 'number', 'Число'
        PREDEFINED = 'predefined', 'Предопределённые значения'

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    value_type = models.CharField(
        'Тип значения', max_length=20, choices=ValueType.choices, default=ValueType.TEXT,
    )
    unit = models.CharField('Единица измерения', max_length=20, blank=True, help_text='мм, шт, мл, мес')
    is_multi = models.BooleanField('Множественный выбор', default=False, help_text='Можно выбрать несколько значений (для predefined)')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CharacteristicValue(models.Model):
    """Предопределённое значение характеристики (для type=predefined)."""
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name='predefined_values',
        verbose_name='Характеристика',
    )
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', max_length=200)
    background = models.ImageField(
        'Фон', upload_to='characteristics/backgrounds/', blank=True,
        help_text='Фоновое изображение (например для ароматов)',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Значение характеристики'
        verbose_name_plural = 'Значения характеристик'
        ordering = ['order', 'name']
        unique_together = ['characteristic', 'slug']

    def __str__(self):
        return f'{self.characteristic.name}: {self.name}'


class CategoryCharacteristic(models.Model):
    """Привязка характеристики к категории с настройками отображения."""

    class DisplayMode(models.TextChoices):
        BLOCK = 'block', 'Блок'
        INLINE = 'inline', 'В строку'

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_characteristics',
        verbose_name='Категория',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name='category_bindings',
        verbose_name='Характеристика',
    )
    is_required = models.BooleanField('Обязательная (для фильтров)', default=False)
    display_mode = models.CharField(
        'Отображение', max_length=10, choices=DisplayMode.choices, default=DisplayMode.BLOCK,
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Характеристика категории'
        verbose_name_plural = 'Характеристики категорий'
        ordering = ['order']
        unique_together = ['category', 'characteristic']

    def __str__(self):
        return f'{self.category.name} → {self.characteristic.name}'


class Product(models.Model):

    class Badge(models.TextChoices):
        BESTSELLER = 'bestseller', 'Хит продаж'
        NEW = 'new', 'Новинка'
        SALE = 'sale', 'Скидка'

    name = models.CharField('Название', max_length=300)
    slug = models.SlugField('Slug', max_length=300, unique=True)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категория',
    )

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

    short_description = models.TextField('Краткое описание', blank=True)
    description = models.TextField('Описание', blank=True)

    badge = models.CharField(
        'Бейдж', max_length=20, choices=Badge.choices, blank=True,
    )
    is_active = models.BooleanField('Активен', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    in_stock = models.BooleanField('В наличии', default=True)

    related_products = models.ManyToManyField(
        'self', symmetrical=False, blank=True, verbose_name='Связанные товары',
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
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug,
        })

    @property
    def has_discount(self):
        return self.old_price is not None and self.old_price > self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            return round((1 - self.price / self.old_price) * 100)
        return 0


class ProductCharacteristic(models.Model):
    """Значение характеристики для конкретного товара."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='characteristics',
        verbose_name='Товар',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name='product_values',
        verbose_name='Характеристика',
    )
    value = models.CharField('Значение', max_length=500, blank=True, help_text='Для text/number типов')
    selected_values = models.ManyToManyField(
        CharacteristicValue,
        blank=True,
        verbose_name='Выбранные значения',
        help_text='Для predefined типа',
    )
    hint = models.CharField('Подсказка', max_length=200, blank=True, help_text='(тоньше волоса)')

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'
        unique_together = ['product', 'characteristic']
        ordering = ['characteristic__order']

    def __str__(self):
        return f'{self.product.name} — {self.characteristic.name}: {self.display_value}'

    @property
    def display_value(self):
        if self.characteristic.value_type == Characteristic.ValueType.PREDEFINED:
            names = list(self.selected_values.order_by('order').values_list('name', flat=True))
            return ', '.join(names)
        if not self.value:
            return ''
        unit = self.characteristic.unit
        return f'{self.value} {unit}'.strip()


class ProductImage(models.Model):

    class ImageType(models.TextChoices):
        MAIN = 'main', 'Основное'
        GALLERY = 'gallery', 'Галерея (каталог)'
        ZOOM = 'zoom', 'Zoom (скролл)'
        SLIDER_PKG = 'slider_pkg', 'Слайдер упаковки'
        SLIDER_IND = 'slider_ind', 'Слайдер индивидуальный'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар',
    )
    image = models.ImageField('Изображение', upload_to='products/%Y/%m/')
    image_type = models.CharField(
        'Тип', max_length=20, choices=ImageType.choices, default=ImageType.GALLERY,
    )
    alt_text = models.CharField('Alt текст', max_length=300, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    rotation_angle = models.IntegerField(
        'Угол поворота (GSAP data-rotate)', default=0,
        help_text='Градус поворота для zoom-эффекта',
    )

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']
        indexes = [
            models.Index(fields=['product', 'image_type']),
        ]

    def __str__(self):
        return f'{self.product.name} — {self.get_image_type_display()}'


class ProductSize(models.Model):

    class Size(models.TextChoices):
        S = 'S', 'S'
        M = 'M', 'M'
        L = 'L', 'L'
        XL = 'XL', 'XL'
        XXL = 'XXL', 'XXL'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sizes',
        verbose_name='Товар',
    )
    size = models.CharField('Размер', max_length=5, choices=Size.choices)
    width_mm = models.PositiveIntegerField('Ширина (мм)', default=0, help_text='Номинальная ширина, например: 52')
    length_mm = models.PositiveIntegerField('Длина (мм)', default=0, help_text='Длина, например: 180')
    is_available = models.BooleanField('В наличии', default=True)
    stock_quantity = models.PositiveIntegerField('Количество на складе', default=0)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Размер товара'
        verbose_name_plural = 'Размеры товаров'
        ordering = ['order']
        unique_together = ['product', 'size']

    def __str__(self):
        return f'{self.product.name} — {self.size}'

    @property
    def dimensions(self):
        return f'{self.width_mm}×{self.length_mm}мм'


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
