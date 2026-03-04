import base64
import logging
import time

import requests
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Кешированный токен
_token_cache = {'token': None, 'expires_at': 0}


def _get_access_token():
    """Получить OAuth-токен SendPulse (кешируется)."""
    now = time.time()
    if _token_cache['token'] and _token_cache['expires_at'] > now:
        return _token_cache['token']

    try:
        resp = requests.post(
            'https://api.sendpulse.com/oauth/access_token',
            json={
                'grant_type': 'client_credentials',
                'client_id': settings.SENDPULSE_API_ID,
                'client_secret': settings.SENDPULSE_API_SECRET,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        _token_cache['token'] = data['access_token']
        _token_cache['expires_at'] = now + data.get('expires_in', 3600) - 60
        return _token_cache['token']
    except Exception as e:
        logger.error('SendPulse auth failed: %s', e)
        return None


def _send(to, subject, template, context):
    """Отправить HTML-письмо через SendPulse API."""
    token = _get_access_token()
    if not token:
        logger.error('Email skipped (no token): %s → %s', template, to)
        return

    try:
        html = render_to_string(f'emails/{template}.html', context)
        html_b64 = base64.b64encode(html.encode('utf-8')).decode('ascii')

        resp = requests.post(
            'https://api.sendpulse.com/smtp/emails',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'email': {
                    'subject': subject,
                    'html': html_b64,
                    'from': {
                        'name': settings.DEFAULT_FROM_NAME,
                        'email': settings.DEFAULT_FROM_EMAIL,
                    },
                    'to': [{'email': to}],
                },
            },
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()

        if result.get('result'):
            logger.info('Email sent: %s → %s (id=%s)', template, to, result.get('id', ''))
        else:
            logger.error('Email rejected: %s → %s: %s', template, to, result)
    except Exception as e:
        logger.error('Email failed: %s → %s: %s', template, to, e)


def send_welcome_email(user):
    """Приветственное письмо после регистрации."""
    _send(
        to=user.email,
        subject='Добро пожаловать в DR.JOYS!',
        template='welcome',
        context={
            'user': user,
            'site_url': settings.PAYMENT_BASE_URL or 'https://dr-joys.com',
        },
    )


def send_order_created_email(order):
    """Письмо о создании заказа (ожидает оплаты)."""
    items = order.items.all()
    _send(
        to=order.customer_email,
        subject=f'Заказ #{order.number} создан — DR.JOYS',
        template='order_created',
        context={
            'order': order,
            'items': items,
            'currency': order.region.currency_symbol,
            'site_url': settings.PAYMENT_BASE_URL or 'https://dr-joys.com',
        },
    )


def send_payment_confirmed_email(order):
    """Письмо о подтверждении оплаты."""
    items = order.items.all()
    _send(
        to=order.customer_email,
        subject=f'Заказ #{order.number} оплачен — DR.JOYS',
        template='order_paid',
        context={
            'order': order,
            'items': items,
            'currency': order.region.currency_symbol,
            'site_url': settings.PAYMENT_BASE_URL or 'https://dr-joys.com',
        },
    )
