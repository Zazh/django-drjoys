from django.core.management.base import BaseCommand

from catalog.models import Category, Product, ProductSize, FAQ


class Command(BaseCommand):
    help = 'Загрузка начальных данных каталога (категория, товары, размеры, FAQ)'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных каталога...')

        # --- Категория ---
        cat, _ = Category.objects.get_or_create(
            slug='prezervativy',
            defaults={
                'name': 'Презервативы',
                'description': 'Презервативы DR.JOYS',
                'order': 1,
                'meta_title': 'Презервативы DR.JOYS — купить онлайн',
                'meta_description': 'Каталог презервативов DR.JOYS — классические, ребристые, ультратонкие',
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Категория: {cat.name}'))

        # --- Товары с размерами ---
        products_data = [
            {
                'slug': 'klassicheskie-banan',
                'name': 'Презервативы DR.JOYS классические, банан',
                'description': (
                    'Гладкая поверхность, латекс бесцветный. С дополнительной '
                    'силиконовой смазкой, с нейтральным ароматом, толщина 0.02 мм '
                    'неощутимые на 95%'
                ),
                'badge': 'bestseller',
                'sizes': [
                    {'name': '3 шт', 'sku': '100001-3', 'price': '2100', 'price_rub': '410'},
                    {'name': '5 шт', 'sku': '100001-5', 'price': '3540', 'old_price': '4200', 'price_rub': '690', 'old_price_rub': '820'},
                    {'name': '12 шт', 'sku': '100001-12', 'price': '7900', 'price_rub': '1540'},
                ],
            },
            {
                'slug': 'klassicheskie',
                'name': 'Презервативы DR.JOYS Классические',
                'description': 'Классические презервативы с гладкой поверхностью.',
                'sizes': [
                    {'name': '3 шт', 'sku': '100002-3', 'price': '2500', 'price_rub': '490'},
                    {'name': '10 шт', 'sku': '100002-10', 'price': '4200', 'price_rub': '820'},
                ],
            },
            {
                'slug': 'rebristye',
                'name': 'Презервативы DR.JOYS Ребристые',
                'description': 'Ребристая текстура для дополнительной стимуляции.',
                'badge': 'new',
                'sizes': [
                    {'name': '3 шт', 'sku': '100003-3', 'price': '2890', 'price_rub': '560'},
                ],
            },
            {
                'slug': 'neoshhutimye',
                'name': 'Презервативы DR.JOYS Неощутимые на 95%',
                'description': 'Ультратонкие, неощутимые на 95%.',
                'sizes': [
                    {'name': '5 шт', 'sku': '100004-5', 'price': '3540', 'price_rub': '690'},
                ],
            },
            {
                'slug': 'xxl',
                'name': 'Презервативы DR.JOYS XXL увеличенные',
                'description': 'Увеличенный размер для максимального комфорта.',
                'sizes': [
                    {'name': '5 шт', 'sku': '100005-5', 'price': '3890', 'old_price': '4500', 'price_rub': '760', 'old_price_rub': '880'},
                ],
            },
        ]

        for data in products_data:
            sizes_data = data.pop('sizes')
            product, created = Product.objects.update_or_create(
                slug=data['slug'],
                defaults={**data, 'category': cat},
            )
            if created:
                self.stdout.write(f'  + {product.name}')
            for i, size in enumerate(sizes_data):
                ProductSize.objects.update_or_create(
                    sku=size['sku'],
                    defaults={**size, 'product': product, 'order': i},
                )

        self.stdout.write(self.style.SUCCESS(f'Товары: {Product.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Размеры: {ProductSize.objects.count()}'))

        # --- FAQ ---
        faqs_data = [
            {
                'question': 'Как подобрать размер презерватива DR.JOYS?',
                'answer': (
                    'Презервативы Dr Joys — это средства барьерной контрацепции, '
                    'разработанные для защиты от нежелательной беременности и инфекций, '
                    'передающихся половым путём.'
                ),
                'order': 1,
            },
            {
                'question': 'Безопасны ли ультратонкие презервативы DR.JOYS?',
                'answer': (
                    'Да, абсолютно безопасны! Каждый презерватив проходит электронное '
                    'тестирование на герметичность и соответствует международным стандартам качества.'
                ),
                'order': 2,
            },
            {
                'question': 'Насколько безопасны презервативы Dr Joys? Есть ли сертификаты качества?',
                'answer': (
                    'Да, абсолютно безопасны! Каждый презерватив проходит электронное '
                    'тестирование на герметичность. Продукция сертифицирована и соответствует '
                    'международным стандартам ISO 4074.'
                ),
                'order': 3,
            },
        ]
        for faq_data in faqs_data:
            FAQ.objects.update_or_create(
                question=faq_data['question'],
                defaults=faq_data,
            )

        self.stdout.write(self.style.SUCCESS(f'FAQ: {FAQ.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('Загрузка завершена!'))
