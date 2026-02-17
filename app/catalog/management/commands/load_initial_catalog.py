from django.core.management.base import BaseCommand

from catalog.models import (
    Category, Characteristic, CharacteristicValue,
    CategoryCharacteristic, Product, ProductCharacteristic,
    ProductSize, FAQ,
)


class Command(BaseCommand):
    help = 'Загрузка начальных данных каталога (категория, характеристики, товары, размеры, FAQ)'

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
        # Переносим товары со старых категорий на новую, затем удаляем старые
        old_cats = Category.objects.filter(slug__in=['klassicheskie', 'rebristye'])
        Product.objects.filter(category__in=old_cats).update(category=cat)
        old_cats.delete()
        self.stdout.write(self.style.SUCCESS(f'Категория: {cat.name}'))

        # --- Характеристики ---
        # (slug, name, value_type, unit, is_multi, order, predefined_values)
        chars_data = [
            ('texture', 'Текстура', 'predefined', '', False, 1, [
                ('gladkaya', 'Гладкая', 1),
                ('rebristaya', 'Ребристая', 2),
            ]),
            ('flavor', 'Аромат', 'predefined', '', True, 2, [
                ('banana', 'Банан', 1),
                ('strawberry', 'Клубника', 2),
                ('chocolate', 'Шоколад', 3),
                ('mint', 'Мята', 4),
                ('vanilla', 'Ваниль', 5),
                ('neutral', 'Нейтральный', 6),
            ]),
            ('thickness', 'Толщина', 'number', 'мм', False, 3, []),
            ('quantity', 'Кол-во в упаковке', 'number', 'шт', False, 4, []),
            ('lubricant-volume', 'Объём смазки', 'number', 'мл', False, 5, []),
            ('shelf-life', 'Срок годности', 'number', 'мес', False, 6, []),
            ('material', 'Материал', 'text', '', False, 7, []),
            ('lubricant-composition', 'Состав смазки', 'text', '', False, 8, []),
            ('country', 'Страна производитель', 'text', '', False, 9, []),
            ('extra', 'Дополнительно', 'text', '', False, 10, []),
        ]

        chars_map = {}  # slug → Characteristic
        vals_map = {}   # (char_slug, val_slug) → CharacteristicValue

        for slug, name, vtype, unit, is_multi, order, predefined in chars_data:
            char, _ = Characteristic.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'value_type': vtype,
                    'unit': unit,
                    'is_multi': is_multi,
                    'order': order,
                },
            )
            chars_map[slug] = char

            for val_slug, val_name, val_order in predefined:
                val, _ = CharacteristicValue.objects.update_or_create(
                    characteristic=char,
                    slug=val_slug,
                    defaults={'name': val_name, 'order': val_order},
                )
                vals_map[(slug, val_slug)] = val

        # Удаляем устаревшие характеристики
        Characteristic.objects.filter(slug='package-contents').delete()

        self.stdout.write(self.style.SUCCESS(f'Характеристики: {Characteristic.objects.count()}'))

        # --- Привязка к категории (is_required + display_mode) ---
        bindings = {
            # slug: (is_required, display_mode)
            'texture':              (True,  'block'),
            'flavor':               (True,  'block'),
            'thickness':            (True,  'block'),
            'quantity':             (True,  'inline'),
            'lubricant-volume':     (False, 'inline'),
            'shelf-life':           (False, 'inline'),
            'material':             (True,  'block'),
            'lubricant-composition': (False, 'block'),
            'country':              (False, 'inline'),
            'extra':                (False, 'block'),
        }
        for slug, (required, mode) in bindings.items():
            char = chars_map[slug]
            CategoryCharacteristic.objects.update_or_create(
                category=cat,
                characteristic=char,
                defaults={
                    'is_required': required,
                    'display_mode': mode,
                    'order': char.order,
                },
            )

        self.stdout.write(self.style.SUCCESS(f'Привязки к категории: {CategoryCharacteristic.objects.count()}'))

        # --- Товары ---
        products_data = [
            {
                'slug': 'banan-002-mm-5-sht',
                'name': 'Презервативы DR.JOYS классические, банан, 0.02 мм, 5 шт.',
                'sku': '100001',
                'price': '3540',
                'old_price': '4200',
                'price_rub': '690',
                'old_price_rub': '820',
                'short_description': (
                    'Гладкая поверхность, латекс бесцветный. С дополнительной '
                    'силиконовой смазкой, с нейтральным ароматом, толщина 0.02 мм '
                    'неощутимые на 95%'
                ),
                'badge': 'bestseller',
                'is_featured': True,
                '_chars': {
                    'texture': {'selected': ['gladkaya']},
                    'flavor': {'selected': ['banana']},
                    'thickness': {'value': '0.02', 'hint': '(тоньше волоса)'},
                    'quantity': {'value': '5'},
                    'shelf-life': {'value': '60'},
                    'material': {'value': 'Натуральный латекс'},
                    'country': {'value': 'Китай'},
                },
            },
            {
                'slug': 'klassicheskie-003-mm-10-sht',
                'name': 'Презервативы DR.JOYS Классические 0.03 мм, 10 шт.',
                'sku': '100002',
                'price': '4200',
                'price_rub': '820',
                'short_description': 'Классические презервативы с гладкой поверхностью.',
                'badge': '',
                '_chars': {
                    'texture': {'selected': ['gladkaya']},
                    'flavor': {'selected': ['neutral']},
                    'thickness': {'value': '0.03'},
                    'quantity': {'value': '10'},
                    'shelf-life': {'value': '60'},
                    'material': {'value': 'Натуральный латекс'},
                    'country': {'value': 'Китай'},
                },
            },
            {
                'slug': 'rebristye-002-mm-3-sht',
                'name': 'Презервативы DR.JOYS Ребристые 0.02 мм, 3 шт.',
                'sku': '100003',
                'price': '2890',
                'price_rub': '560',
                'short_description': 'Ребристая текстура для дополнительной стимуляции.',
                'badge': 'new',
                '_chars': {
                    'texture': {'selected': ['rebristaya']},
                    'flavor': {'selected': ['strawberry', 'chocolate']},
                    'thickness': {'value': '0.02', 'hint': '(тоньше волоса)'},
                    'quantity': {'value': '3'},
                    'shelf-life': {'value': '60'},
                    'material': {'value': 'Натуральный латекс'},
                    'country': {'value': 'Китай'},
                },
            },
            {
                'slug': 'neoshhutimye-002-mm-5-sht',
                'name': 'Презервативы DR.JOYS Неощутимые на 95% 0.02 мм, 5 шт.',
                'sku': '100004',
                'price': '3540',
                'price_rub': '690',
                'short_description': 'Ультратонкие, неощутимые на 95%.',
                'badge': '',
                '_chars': {
                    'texture': {'selected': ['gladkaya']},
                    'flavor': {'selected': ['neutral']},
                    'thickness': {'value': '0.02', 'hint': '(неощутимые на 95%)'},
                    'quantity': {'value': '5'},
                    'shelf-life': {'value': '60'},
                    'material': {'value': 'Натуральный латекс'},
                    'country': {'value': 'Китай'},
                },
            },
            {
                'slug': 'xxl-003-mm-5-sht',
                'name': 'Презервативы DR.JOYS XXL увеличенные 0.03 мм, 5 шт.',
                'sku': '100005',
                'price': '3890',
                'old_price': '4500',
                'price_rub': '760',
                'old_price_rub': '880',
                'short_description': 'Увеличенный размер для максимального комфорта.',
                'badge': '',
                '_chars': {
                    'texture': {'selected': ['gladkaya']},
                    'flavor': {'selected': ['banana', 'mint', 'vanilla']},
                    'thickness': {'value': '0.03'},
                    'quantity': {'value': '5'},
                    'shelf-life': {'value': '60'},
                    'material': {'value': 'Натуральный латекс'},
                    'country': {'value': 'Китай'},
                },
            },
        ]

        created_products = []
        for data in products_data:
            chars_spec = data.pop('_chars')
            product, created = Product.objects.update_or_create(
                slug=data['slug'],
                defaults={**data, 'category': cat},
            )
            created_products.append(product)

            for char_slug, spec in chars_spec.items():
                char = chars_map[char_slug]
                pc, _ = ProductCharacteristic.objects.update_or_create(
                    product=product,
                    characteristic=char,
                    defaults={
                        'value': spec.get('value', ''),
                        'hint': spec.get('hint', ''),
                    },
                )
                if 'selected' in spec:
                    val_objs = [vals_map[(char_slug, vs)] for vs in spec['selected']]
                    pc.selected_values.set(val_objs)

            if created:
                self.stdout.write(f'  + {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Товары: {Product.objects.count()}'))

        # --- Размеры ---
        size_defaults = [
            {'size': 'M', 'width_mm': 52, 'length_mm': 180, 'is_available': True, 'stock_quantity': 100, 'order': 1},
            {'size': 'L', 'width_mm': 54, 'length_mm': 190, 'is_available': True, 'stock_quantity': 80, 'order': 2},
            {'size': 'XL', 'width_mm': 56, 'length_mm': 200, 'is_available': False, 'stock_quantity': 0, 'order': 3},
        ]
        for product in created_products:
            for sd in size_defaults:
                ProductSize.objects.update_or_create(
                    product=product,
                    size=sd['size'],
                    defaults=sd,
                )

        self.stdout.write(self.style.SUCCESS(f'Размеры: {ProductSize.objects.count()}'))

        # --- Связанные товары ---
        for product in created_products:
            others = [p for p in created_products if p.pk != product.pk]
            product.related_products.set(others)

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
