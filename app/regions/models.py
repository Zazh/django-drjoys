from django.db import models


class Region(models.Model):
    """Регион продажи (страна) с привязкой к валюте."""

    code = models.CharField(
        'Код', max_length=5, unique=True,
        help_text='ISO-код: kz, ru, uz, kg, int',
    )
    name = models.CharField('Название', max_length=100)
    currency_code = models.CharField(
        'Код валюты', max_length=3,
        help_text='ISO 4217: KZT, RUB, UZS, USD',
    )
    currency_symbol = models.CharField(
        'Символ валюты', max_length=5,
        help_text='₸, ₽, $',
    )
    default_language = models.CharField(
        'Язык по умолчанию', max_length=5, default='ru',
    )
    phone_code = models.CharField(
        'Телефонный код', max_length=5, default='+7',
    )
    flag_emoji = models.CharField(
        'Флаг', max_length=10, blank=True,
        help_text='Emoji: \U0001f1f0\U0001f1ff, \U0001f1f7\U0001f1fa',
    )
    is_active = models.BooleanField('Активен', default=True)
    is_default = models.BooleanField(
        'По умолчанию', default=False,
        help_text='Только один регион может быть по умолчанию',
    )
    payment_gateway = models.CharField(
        'Платёжный шлюз', max_length=20, blank=True,
        help_text='Код шлюза: vtb, halyk. Пусто = без онлайн-оплаты',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_region',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.currency_code})'

    @classmethod
    def get_default(cls):
        """Возвращает регион по умолчанию."""
        return cls.objects.filter(is_default=True, is_active=True).first()
