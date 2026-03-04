from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def region_price(context, size, field='price'):
    """
    Возвращает цену размера для текущего региона.

    Использование:
        {% region_price size 'price' as rprice %}
        {% region_price size 'old_price' as old_rprice %}

    Сначала ищет RegionPrice (prefetched), если нет — fallback на базовую цену ProductSize.
    """
    request = context.get('request')
    region = getattr(request, 'region', None)

    if region:
        # Prefetched region prices (to_attr='_region_prices')
        region_prices = getattr(size, '_region_prices', None)
        if region_prices is not None:
            for rp in region_prices:
                if rp.region_id == region.pk:
                    return getattr(rp, field, None)
        else:
            # Fallback: DB query (non-prefetched)
            try:
                rp = size.region_prices.get(region=region)
                return getattr(rp, field, None)
            except size.region_prices.model.DoesNotExist:
                pass

    # Fallback: base price on ProductSize
    return getattr(size, field, None)


@register.simple_tag(takes_context=True)
def region_price_data(context, size):
    """
    Возвращает dict с price, old_price, has_discount, discount_percent для текущего региона.
    Если у региона needs_conversion — добавляет payment_price, payment_old_price, payment_currency_symbol.

    Использование:
        {% region_price_data size as pd %}
        {{ pd.price }} {{ pd.old_price }} {{ pd.has_discount }} {{ pd.discount_percent }}
        {% if pd.needs_conversion %}({{ pd.payment_price }} {{ pd.payment_currency_symbol }}){% endif %}
    """
    request = context.get('request')
    region = getattr(request, 'region', None)

    data = None
    if region:
        region_prices = getattr(size, '_region_prices', None)
        if region_prices is not None:
            for rp in region_prices:
                if rp.region_id == region.pk:
                    data = {
                        'price': rp.price,
                        'old_price': rp.old_price,
                        'has_discount': rp.has_discount,
                        'discount_percent': rp.discount_percent,
                    }
                    break
        else:
            try:
                rp = size.region_prices.get(region=region)
                data = {
                    'price': rp.price,
                    'old_price': rp.old_price,
                    'has_discount': rp.has_discount,
                    'discount_percent': rp.discount_percent,
                }
            except size.region_prices.model.DoesNotExist:
                pass

    if data is None:
        data = {
            'price': size.price,
            'old_price': size.old_price,
            'has_discount': size.has_discount,
            'discount_percent': size.discount_percent,
        }

    # Двойная валюта: если у региона payment_currency отличается
    if region and region.needs_conversion:
        from regions.models import convert_to_kzt
        data['needs_conversion'] = True
        data['payment_price'] = convert_to_kzt(data['price'], region.currency_code)
        data['payment_old_price'] = convert_to_kzt(data['old_price'], region.currency_code) if data['old_price'] else None
        data['payment_currency_symbol'] = region.payment_currency_symbol
    else:
        data['needs_conversion'] = False

    return data


@register.filter
def format_price(value):
    """Форматирует цену: без десятичных, пробелы-разделители тысяч."""
    if value is None:
        return ''
    try:
        num = int(value)
        return f'{num:,}'.replace(',', ' ')
    except (ValueError, TypeError):
        return str(value)
