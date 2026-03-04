import json
import logging
from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from catalog.models import ProductSize, RegionPrice, Stock
from .cart import Cart, Favorites
from .emails import send_order_created_email
from .forms import CheckoutForm
from .gateways import get_gateway, get_gateway_by_code
from .models import Order, OrderItem

logger = logging.getLogger(__name__)


def _json_body(request):
    content_type = request.content_type or ''
    if 'application/json' in content_type:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    return request.POST


# ─── Корзина ───

class CartView(View):
    """GET /orders/cart/ — получить содержимое корзины."""

    def get(self, request):
        cart = Cart(request)
        items = cart.get_items()
        cart_total = Decimal('0')
        cart_old_total = Decimal('0')
        serialized = []
        for item in items:
            cart_total += item['subtotal']
            old_p = item['old_price'] or item['price']
            cart_old_total += old_p * item['qty']
            s = {
                'size_id': item['size_id'],
                'qty': item['qty'],
                'name': item['name'],
                'size_name': item['size_name'],
                'sku': item['sku'],
                'price': str(item['price']),
                'old_price': str(item['old_price']) if item['old_price'] else None,
                'subtotal': str(item['subtotal']),
                'image_url': item['image_url'],
                'product_url': item['product_url'],
            }
            if 'payment_price' in item:
                s['payment_price'] = str(item['payment_price'])
                s['payment_subtotal'] = str(item['payment_subtotal'])
            serialized.append(s)

        resp = {
            'ok': True,
            'items': serialized,
            'cart_total': str(cart_total),
            'cart_old_total': str(cart_old_total),
            'cart_count': len(cart),
        }
        payment_total = cart.get_payment_total()
        if payment_total != cart_total:
            resp['payment_total'] = str(payment_total)
        return JsonResponse(resp)


class CartAddView(View):
    """POST /orders/cart/add/ — добавить товар в корзину."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        size_id = data.get('size_id')
        qty = int(data.get('qty', 1))

        if not size_id:
            return JsonResponse(
                {'ok': False, 'error': 'size_id обязателен'},
                status=400,
            )

        if not ProductSize.objects.filter(pk=size_id).exists():
            return JsonResponse(
                {'ok': False, 'error': 'Размер не найден'},
                status=404,
            )

        cart = Cart(request)
        cart.add(int(size_id), qty)

        return JsonResponse({
            'ok': True,
            'cart_count': len(cart),
            'item': cart.get_item(int(size_id)),
        })


class CartRemoveView(View):
    """POST /orders/cart/remove/ — удалить товар из корзины."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        size_id = data.get('size_id')

        if not size_id:
            return JsonResponse(
                {'ok': False, 'error': 'size_id обязателен'},
                status=400,
            )

        cart = Cart(request)
        cart.remove(int(size_id))

        return JsonResponse({
            'ok': True,
            'cart_count': len(cart),
        })


class CartUpdateView(View):
    """POST /orders/cart/update/ — обновить количество."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        size_id = data.get('size_id')
        qty = data.get('qty')

        if not size_id or qty is None:
            return JsonResponse(
                {'ok': False, 'error': 'size_id и qty обязательны'},
                status=400,
            )

        cart = Cart(request)
        cart.update(int(size_id), int(qty))

        # Пересчитать total
        items = cart.get_items()
        cart_total = sum(i['subtotal'] for i in items)

        return JsonResponse({
            'ok': True,
            'cart_count': len(cart),
            'item': cart.get_item(int(size_id)),
            'cart_total': str(cart_total),
        })


# ─── Избранное ───

class FavoritesView(View):
    """GET /orders/favorites/ — получить избранное."""

    def get(self, request):
        favs = Favorites(request)
        items = favs.get_items()
        serialized = []
        for item in items:
            s = {
                'product_id': item['product_id'],
                'name': item['name'],
                'slug': item['slug'],
                'price': str(item['price']) if item['price'] else None,
                'old_price': str(item['old_price']) if item['old_price'] else None,
                'image_url': item['image_url'],
                'product_url': item['product_url'],
                'first_size_id': item['first_size_id'],
            }
            if 'payment_price' in item and item['payment_price'] is not None:
                s['payment_price'] = str(item['payment_price'])
            serialized.append(s)
        return JsonResponse({
            'ok': True,
            'items': serialized,
            'fav_count': len(favs),
        })


class FavoritesAddView(View):
    """POST /orders/favorites/add/ — добавить в избранное."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse(
                {'ok': False, 'error': 'product_id обязателен'},
                status=400,
            )

        favs = Favorites(request)
        favs.add(int(product_id))

        return JsonResponse({
            'ok': True,
            'fav_count': len(favs),
        })


class FavoritesRemoveView(View):
    """POST /orders/favorites/remove/ — удалить из избранного."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse(
                {'ok': False, 'error': 'product_id обязателен'},
                status=400,
            )

        favs = Favorites(request)
        favs.remove(int(product_id))

        return JsonResponse({
            'ok': True,
            'fav_count': len(favs),
        })


class FavoritesToggleView(View):
    """POST /orders/favorites/toggle/ — toggle избранного."""

    @method_decorator(csrf_protect)
    def post(self, request):
        data = _json_body(request)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse(
                {'ok': False, 'error': 'product_id обязателен'},
                status=400,
            )

        favs = Favorites(request)
        added = favs.toggle(int(product_id))

        return JsonResponse({
            'ok': True,
            'added': added,
            'fav_count': len(favs),
        })


# ─── Оформление заказа ───

class CheckoutView(View):
    """GET /orders/checkout/ — страница оформления заказа.
    POST /orders/checkout/ — создать заказ (form или JSON API).
    """

    def get(self, request):
        cart = Cart(request)
        if not cart:
            return redirect(reverse('catalog:catalog'))

        cart_items = cart.get_items()
        cart_total = sum(i['subtotal'] for i in cart_items)
        cart_old_total = sum(
            (i['old_price'] or i['price']) * i['qty'] for i in cart_items
        )

        initial = {}
        if request.user.is_authenticated:
            user = request.user
            initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': getattr(user, 'phone', ''),
                'email': user.email,
                'country': request.region.code if request.region else '',
            }

        form = CheckoutForm(initial=initial)

        ctx = {
            'form': form,
            'cart_items': cart_items,
            'cart_total': cart_total,
            'cart_old_total': cart_old_total,
            'is_authenticated': request.user.is_authenticated,
        }
        # Двойная валюта
        if request.region and request.region.needs_conversion:
            ctx['payment_total'] = cart.get_payment_total()
        return render(request, 'orders/checkout.html', ctx)

    @method_decorator(csrf_protect)
    def post(self, request):
        # JSON API — backward compatibility (модалка, JS)
        if 'application/json' in (request.content_type or ''):
            return self._handle_json_checkout(request)
        # Стандартная форма со страницы checkout
        return self._handle_form_checkout(request)

    def _handle_form_checkout(self, request):
        """POST со страницы checkout (стандартная HTML-форма)."""
        cart = Cart(request)
        cart_items = cart.get_items()
        cart_total = sum(i['subtotal'] for i in cart_items)
        cart_old_total = sum(
            (i['old_price'] or i['price']) * i['qty'] for i in cart_items
        )

        def _render_with_error(form, error_message=None):
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'cart_total': cart_total,
                'cart_old_total': cart_old_total,
                'is_authenticated': request.user.is_authenticated,
                'error_message': error_message,
            })

        if not request.user.is_authenticated:
            return redirect('/orders/checkout/')

        if not cart:
            return redirect(reverse('catalog:catalog'))

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return _render_with_error(form)

        region = request.region
        if not region:
            return _render_with_error(form, 'Регион не определён')

        if not cart_items:
            return _render_with_error(form, 'Товары в корзине не найдены')

        cd = form.cleaned_data
        first_name = cd['first_name']
        last_name = cd['last_name']
        phone = cd['phone']
        email = cd.get('email', '')
        city = cd['city']
        address = form.get_address()
        total = cart_total

        try:
            order = self._create_order(
                request, region, first_name, last_name, phone, email,
                city, address, total, cart_items,
            )
        except ValueError as e:
            return _render_with_error(form, str(e))

        self._update_user_profile(request.user, first_name, last_name, phone)

        # Оплата
        payment_url = self._register_payment(request, order, cart)
        if payment_url is None:
            # Ошибка шлюза — заказ отменён
            return _render_with_error(form, 'Ошибка платёжной системы. Попробуйте позже.')
        elif payment_url:
            # Есть ссылка на оплату
            return redirect(payment_url)
        else:
            # Регион без онлайн-оплаты
            cart.clear()
            send_order_created_email(order)
            return redirect(reverse(
                'orders:checkout_success',
                kwargs={'order_number': order.number},
            ))

    def _handle_json_checkout(self, request):
        """POST JSON API — backward compat для модалки."""
        if not request.user.is_authenticated:
            return JsonResponse(
                {'ok': False, 'error': 'auth_required'},
                status=401,
            )

        data = _json_body(request)
        cart = Cart(request)

        if not cart:
            return JsonResponse(
                {'ok': False, 'error': 'Корзина пуста'},
                status=400,
            )

        # Валидация полей
        errors = {}
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        phone = (data.get('phone') or '').strip()
        email = (data.get('email') or '').strip()
        city = (data.get('city') or '').strip()
        address = (data.get('address') or '').strip()

        if not first_name:
            errors['first_name'] = 'Укажите имя'
        if not last_name:
            errors['last_name'] = 'Укажите фамилию'
        if not phone:
            errors['phone'] = 'Укажите телефон'
        if not city:
            errors['city'] = 'Укажите город'
        if not address:
            errors['address'] = 'Укажите адрес'

        if errors:
            return JsonResponse({'ok': False, 'errors': errors}, status=400)

        region = request.region
        if not region:
            return JsonResponse(
                {'ok': False, 'error': 'Регион не определён'},
                status=400,
            )

        cart_items = cart.get_items()
        if not cart_items:
            return JsonResponse(
                {'ok': False, 'error': 'Товары в корзине не найдены'},
                status=400,
            )

        total = sum(i['subtotal'] for i in cart_items)

        try:
            order = self._create_order(
                request, region, first_name, last_name, phone, email,
                city, address, total, cart_items,
            )
        except ValueError as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

        self._update_user_profile(request.user, first_name, last_name, phone)

        payment_url = self._register_payment(request, order, cart)
        if payment_url is None:
            return JsonResponse({
                'ok': False,
                'error': 'Ошибка платёжной системы. Попробуйте позже.',
            }, status=502)
        elif payment_url:
            return JsonResponse({
                'ok': True,
                'order_number': order.number,
                'total': str(total),
                'payment_url': payment_url,
            })
        else:
            cart.clear()
            send_order_created_email(order)
            return JsonResponse({
                'ok': True,
                'order_number': order.number,
                'total': str(total),
            })

    # ─── Общие helpers ───

    def _create_order(self, request, region, first_name, last_name,
                      phone, email, city, address, total, cart_items):
        """Создать заказ + позиции + зарезервировать stock. Raises ValueError."""
        # Конвертация в валюту оплаты (если нужно)
        order_kwargs = {
            'region': region,
            'user': request.user,
            'customer_name': f'{first_name} {last_name}',
            'customer_phone': phone,
            'customer_email': email or request.user.email,
            'city': city,
            'address': address,
            'expires_at': timezone.now() + timedelta(minutes=30),
        }

        if region.needs_conversion:
            from regions.models import ExchangeRate, convert_to_kzt
            payment_total = convert_to_kzt(total, region.currency_code)
            rate_obj = ExchangeRate.objects.get(currency_code=region.currency_code)
            order_kwargs['total_amount'] = payment_total
            order_kwargs['display_amount'] = total
            order_kwargs['display_currency_code'] = region.currency_code
            order_kwargs['exchange_rate_snapshot'] = rate_obj.rate / rate_obj.quant
        else:
            order_kwargs['total_amount'] = total

        with transaction.atomic():
            order = Order.objects.create(**order_kwargs)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    size_id=item['size_id'],
                    product_name=item['name'],
                    size_name=item['size_name'],
                    quantity=item['qty'],
                    price=item['price'],
                )

            for item in cart_items:
                try:
                    stock = Stock.objects.select_for_update().get(
                        size_id=item['size_id'], region=region,
                    )
                except Stock.DoesNotExist:
                    raise ValueError(
                        f'{item["name"]} ({item["size_name"]}) — нет в наличии'
                    )
                if stock.available < item['qty']:
                    raise ValueError(
                        f'{item["name"]} ({item["size_name"]}) — недостаточно на складе'
                    )
                stock.reserved += item['qty']
                stock.save(update_fields=['reserved', 'updated_at'])

        return order

    def _update_user_profile(self, user, first_name, last_name, phone):
        """Сохранить данные в профиль, если ещё не заполнены."""
        updated = []
        if first_name and not user.first_name:
            user.first_name = first_name
            updated.append('first_name')
        if last_name and not user.last_name:
            user.last_name = last_name
            updated.append('last_name')
        if phone and not getattr(user, 'phone', None):
            user.phone = phone
            updated.append('phone')
        if updated:
            user.save(update_fields=updated)

    def _register_payment(self, request, order, cart):
        """Зарегистрировать платёж. Returns: url (str), '' (no gateway), None (error)."""
        region = order.region
        gateway = get_gateway(region)
        if not gateway:
            return ''  # Регион без онлайн-оплаты

        base = settings.PAYMENT_BASE_URL or ''
        if base:
            return_url = base.rstrip('/') + '/orders/payment/return/'
            callback_url = base.rstrip('/') + f'/orders/payment/callback/{gateway.code}/'
        else:
            return_url = request.build_absolute_uri('/orders/payment/return/')
            callback_url = request.build_absolute_uri(
                f'/orders/payment/callback/{gateway.code}/'
            )

        result = gateway.create_payment(order, return_url, callback_url)

        if result.success:
            order.payment_gateway = gateway.code
            order.payment_id = result.payment_id

            if result.payment_url == '__halyk__':
                request.session['halyk_payment'] = result._payment_object
                payment_url = request.build_absolute_uri(
                    f'/orders/payment/halyk-pay/{order.number}/'
                )
            else:
                payment_url = result.payment_url

            order.payment_url = payment_url
            order.save(update_fields=[
                'payment_gateway', 'payment_id', 'payment_url',
            ])
            cart.clear()
            send_order_created_email(order)
            return payment_url

        logger.error(
            'Payment failed for order %s (%s): %s',
            order.number, gateway.code, result.error_message,
        )
        order.cancel()
        return None  # Ошибка


class CheckoutSuccessView(View):
    """GET /orders/checkout/success/<order_number>/ — заказ оформлен."""

    def get(self, request, order_number):
        try:
            order = Order.objects.select_related('region').get(
                number=order_number,
            )
        except Order.DoesNotExist:
            return redirect('/')

        # Показать только владельцу заказа
        if request.user.is_authenticated and order.user_id and order.user != request.user:
            return redirect('/')

        return render(request, 'orders/checkout_success.html', {
            'order': order,
            'currency_symbol': order.region.currency_symbol,
        })


# ─── Оплата ───

class PaymentReturnView(View):
    """GET /orders/payment/return/ — шлюз редиректит сюда после оплаты."""

    def get(self, request):
        # Найти заказ по payment_id из GET-параметров
        # VTB шлёт orderId, Halyk шлёт invoiceId — пробуем оба
        payment_id = (
            request.GET.get('orderId')
            or request.GET.get('invoiceId', '')
        )

        if not payment_id:
            return render(request, 'orders/payment_result.html', {
                'success': False,
                'error_message': 'Некорректная ссылка',
            })

        try:
            order = Order.objects.select_related('region').get(
                payment_id=payment_id,
            )
        except Order.DoesNotExist:
            return render(request, 'orders/payment_result.html', {
                'success': False,
                'error_message': 'Заказ не найден',
            })

        # Проверить статус через шлюз
        if order.payment_gateway and order.status == Order.Status.PENDING:
            try:
                gateway = get_gateway_by_code(order.payment_gateway)
                status = gateway.check_status(order.payment_id)
                if status.paid:
                    order.confirm_payment()
            except (KeyError, Exception) as e:
                logger.error('Payment return check failed: %s', e)

        return render(request, 'orders/payment_result.html', {
            'success': order.status == Order.Status.PAID,
            'order': order,
            'currency_symbol': order.region.currency_symbol,
        })


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """POST/GET /orders/payment/callback/<gateway_code>/ — серверный callback."""

    def post(self, request, gateway_code):
        return self._handle(request, gateway_code)

    def get(self, request, gateway_code):
        return self._handle(request, gateway_code)

    def _handle(self, request, gateway_code):
        try:
            gateway = get_gateway_by_code(gateway_code)
        except KeyError:
            return HttpResponse('unknown gateway', status=404)

        order, paid = gateway.process_callback(request)

        if order and paid and order.status == Order.Status.PENDING:
            order.confirm_payment()
            logger.info('Callback confirmed: order %s via %s', order.number, gateway_code)

        return HttpResponse('OK', status=200)


class HalykPayView(View):
    """GET /orders/payment/halyk-pay/<order_number>/ — промежуточная страница с halyk.pay() JS."""

    def get(self, request, order_number):
        payment_object = request.session.pop('halyk_payment', None)
        if not payment_object:
            return render(request, 'orders/payment_result.html', {
                'success': False,
                'error_message': 'Сессия оплаты истекла. Попробуйте оформить заказ заново.',
            })

        return render(request, 'orders/halyk_redirect.html', {
            'payment_object_json': payment_object,
            'halyk_js_url': settings.HALYK_PAYMENT_URL.rstrip('/') + '/payform/payment-api.js',
        })
