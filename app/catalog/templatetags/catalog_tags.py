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

    Использование:
        {% region_price_data size as pd %}
        {{ pd.price }} {{ pd.old_price }} {{ pd.has_discount }} {{ pd.discount_percent }}
    """
    request = context.get('request')
    region = getattr(request, 'region', None)

    if region:
        region_prices = getattr(size, '_region_prices', None)
        if region_prices is not None:
            for rp in region_prices:
                if rp.region_id == region.pk:
                    return {
                        'price': rp.price,
                        'old_price': rp.old_price,
                        'has_discount': rp.has_discount,
                        'discount_percent': rp.discount_percent,
                    }
        else:
            try:
                rp = size.region_prices.get(region=region)
                return {
                    'price': rp.price,
                    'old_price': rp.old_price,
                    'has_discount': rp.has_discount,
                    'discount_percent': rp.discount_percent,
                }
            except size.region_prices.model.DoesNotExist:
                pass

    return {
        'price': size.price,
        'old_price': size.old_price,
        'has_discount': size.has_discount,
        'discount_percent': size.discount_percent,
    }


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
