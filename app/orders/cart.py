from decimal import Decimal

from catalog.models import ProductSize, RegionPrice, Product


CART_SESSION_KEY = 'cart'
FAVORITES_SESSION_KEY = 'favorites'


class Cart:
    """Корзина на основе сессии. Ключ — str(size_id), значение — qty."""

    def __init__(self, request):
        self.session = request.session
        self.region = getattr(request, 'region', None)
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[CART_SESSION_KEY] = cart
        self.cart = cart

    def add(self, size_id, qty=1):
        key = str(size_id)
        self.cart[key] = self.cart.get(key, 0) + qty
        self._save()

    def remove(self, size_id):
        key = str(size_id)
        if key in self.cart:
            del self.cart[key]
            self._save()

    def update(self, size_id, qty):
        key = str(size_id)
        if qty > 0:
            self.cart[key] = qty
        else:
            self.cart.pop(key, None)
        self._save()

    def clear(self):
        self.cart.clear()
        self._save()

    def _save(self):
        self.session.modified = True

    def __len__(self):
        return sum(self.cart.values())

    def __bool__(self):
        return bool(self.cart)

    def get_items(self):
        """Загрузить данные о товарах из БД с региональными ценами."""
        size_ids = [int(k) for k in self.cart.keys()]
        if not size_ids:
            return []

        sizes = (
            ProductSize.objects
            .filter(pk__in=size_ids)
            .select_related('product', 'product__category')
        )
        sizes_map = {s.pk: s for s in sizes}

        # Региональные цены
        prices_map = {}
        if self.region:
            region_prices = RegionPrice.objects.filter(
                size_id__in=size_ids, region=self.region,
            )
            prices_map = {rp.size_id: rp for rp in region_prices}

        items = []
        for key, qty in self.cart.items():
            size_id = int(key)
            size = sizes_map.get(size_id)
            if not size:
                continue

            rp = prices_map.get(size_id)
            price = rp.price if rp else size.price
            old_price = (rp.old_price if rp else size.old_price) or None

            cover = size.product.main_images.filter(is_cover=True).first()
            image_url = cover.thumbnail.url if cover and cover.thumbnail else (
                cover.image.url if cover else ''
            )

            items.append({
                'size_id': size_id,
                'qty': qty,
                'name': str(size.product.name),
                'size_name': size.name,
                'sku': size.sku,
                'price': price,
                'old_price': old_price,
                'subtotal': price * qty,
                'image_url': image_url,
                'product_url': size.product.get_absolute_url(),
            })
        return items

    def get_total(self):
        items = self.get_items()
        return sum(i['subtotal'] for i in items)

    def get_old_total(self):
        items = self.get_items()
        total = Decimal('0')
        for i in items:
            p = i['old_price'] or i['price']
            total += p * i['qty']
        return total

    def get_item(self, size_id):
        """Одна позиция для ответа add/update."""
        key = str(size_id)
        qty = self.cart.get(key, 0)
        if not qty:
            return None

        size = (
            ProductSize.objects
            .filter(pk=size_id)
            .select_related('product')
            .first()
        )
        if not size:
            return None

        rp = None
        if self.region:
            rp = RegionPrice.objects.filter(
                size=size, region=self.region,
            ).first()

        price = rp.price if rp else size.price
        old_price = (rp.old_price if rp else size.old_price) or None

        return {
            'size_id': size_id,
            'qty': qty,
            'name': str(size.product.name),
            'size_name': size.name,
            'price': str(price),
            'old_price': str(old_price) if old_price else None,
            'subtotal': str(price * qty),
        }


class Favorites:
    """Избранное на основе сессии. Хранит список product_id."""

    def __init__(self, request):
        self.session = request.session
        self.region = getattr(request, 'region', None)
        favs = self.session.get(FAVORITES_SESSION_KEY)
        if favs is None:
            favs = []
            self.session[FAVORITES_SESSION_KEY] = favs
        self.favorites = favs

    def add(self, product_id):
        pid = int(product_id)
        if pid not in self.favorites:
            self.favorites.append(pid)
            self._save()

    def remove(self, product_id):
        pid = int(product_id)
        if pid in self.favorites:
            self.favorites.remove(pid)
            self._save()

    def toggle(self, product_id):
        """Toggle: add/remove. Returns True if added, False if removed."""
        pid = int(product_id)
        if pid in self.favorites:
            self.favorites.remove(pid)
            self._save()
            return False
        else:
            self.favorites.append(pid)
            self._save()
            return True

    def _save(self):
        self.session.modified = True

    def __contains__(self, product_id):
        return int(product_id) in self.favorites

    def __len__(self):
        return len(self.favorites)

    def __bool__(self):
        return bool(self.favorites)

    def get_items(self):
        """Загрузить товары из БД с ценами первого размера."""
        if not self.favorites:
            return []

        products = (
            Product.objects
            .filter(pk__in=self.favorites, is_active=True)
            .select_related('category')
            .prefetch_related('sizes', 'main_images')
        )

        items = []
        for product in products:
            first_size = product.sizes.first()
            price = None
            old_price = None

            if first_size and self.region:
                rp = RegionPrice.objects.filter(
                    size=first_size, region=self.region,
                ).first()
                if rp:
                    price = rp.price
                    old_price = rp.old_price
            if first_size and price is None:
                price = first_size.price
                old_price = first_size.old_price

            cover = product.main_images.filter(is_cover=True).first()
            image_url = cover.thumbnail.url if cover and cover.thumbnail else (
                cover.image.url if cover else ''
            )

            items.append({
                'product_id': product.pk,
                'name': str(product.name),
                'slug': product.slug,
                'price': price,
                'old_price': old_price or None,
                'image_url': image_url,
                'product_url': product.get_absolute_url(),
                'first_size_id': first_size.pk if first_size else None,
            })
        return items
