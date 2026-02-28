from django.db import models, transaction
from django.utils import timezone

from catalog.models import ProductSize, Stock
from regions.models import Region


class Order(models.Model):
    """Заказ в интернет-магазине."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'
        EXPIRED = 'expired', 'Истёк'

    number = models.CharField('Номер', max_length=20, unique=True, editable=False)
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT,
        related_name='orders', verbose_name='Регион',
    )

    # Покупатель
    customer_name = models.CharField('ФИО', max_length=200)
    customer_phone = models.CharField('Телефон', max_length=20)
    customer_email = models.EmailField('Email', blank=True)

    # Доставка
    city = models.CharField('Город', max_length=100)
    address = models.TextField('Адрес')

    # Оплата
    payment_id = models.CharField('ID платежа', max_length=200, blank=True,
        help_text='ID транзакции от эквайринга',
    )
    payment_url = models.URLField('Ссылка на оплату', blank=True)
    total_amount = models.DecimalField('Сумма заказа', max_digits=10, decimal_places=2)

    # Даты
    expires_at = models.DateTimeField('Истекает',
        help_text='Срок действия счёта на оплату',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    paid_at = models.DateTimeField('Оплачен', null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Заказ #{self.number}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        """Генерация номера заказа: YYMMDD-XXXX."""
        today = timezone.now().strftime('%y%m%d')
        last = (
            Order.objects
            .filter(number__startswith=today)
            .order_by('-number')
            .values_list('number', flat=True)
            .first()
        )
        if last:
            seq = int(last.split('-')[1]) + 1
        else:
            seq = 1
        return f'{today}-{seq:04d}'

    # ─── Бизнес-логика ───

    @transaction.atomic
    def reserve_stock(self):
        """Зарезервировать товар на складе при создании заказа."""
        for item in self.items.select_related('size'):
            stock = Stock.objects.select_for_update().get(
                size=item.size, region=self.region,
            )
            stock.reserved += item.quantity
            stock.save(update_fields=['reserved', 'updated_at'])

    @transaction.atomic
    def release_stock(self):
        """Снять резерв (заказ отменён или истёк)."""
        for item in self.items.select_related('size'):
            try:
                stock = Stock.objects.select_for_update().get(
                    size=item.size, region=self.region,
                )
                stock.reserved = max(0, stock.reserved - item.quantity)
                stock.save(update_fields=['reserved', 'updated_at'])
            except Stock.DoesNotExist:
                pass

    @transaction.atomic
    def confirm_payment(self):
        """Оплата подтверждена — списать со склада."""
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])

        for item in self.items.select_related('size'):
            try:
                stock = Stock.objects.select_for_update().get(
                    size=item.size, region=self.region,
                )
                stock.quantity = max(0, stock.quantity - item.quantity)
                stock.reserved = max(0, stock.reserved - item.quantity)
                stock.save(update_fields=['quantity', 'reserved', 'updated_at'])
            except Stock.DoesNotExist:
                pass

    def cancel(self):
        """Отменить заказ — снять резерв."""
        self.release_stock()
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status'])

    def expire(self):
        """Заказ истёк — снять резерв."""
        self.release_stock()
        self.status = self.Status.EXPIRED
        self.save(update_fields=['status'])


class OrderItem(models.Model):
    """Позиция в заказе."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Заказ',
    )
    size = models.ForeignKey(
        ProductSize, on_delete=models.PROTECT,
        related_name='order_items', verbose_name='Размер',
    )
    # Фиксируем на момент заказа
    product_name = models.CharField('Название товара', max_length=300)
    size_name = models.CharField('Размер', max_length=50)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена за ед.', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product_name} ({self.size_name}) × {self.quantity}'

    @property
    def subtotal(self):
        return self.price * self.quantity
