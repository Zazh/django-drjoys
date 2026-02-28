from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Region


@admin.register(Region)
class RegionAdmin(TabbedTranslationAdmin):
    list_display = (
        'code', 'name', 'flag_emoji', 'currency_code',
        'currency_symbol', 'default_language', 'is_active',
        'is_default', 'order',
    )
    list_editable = ('is_active', 'is_default', 'order')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # При создании/активации региона — создать RegionPrice + Stock для всех размеров
        if obj.is_active:
            from catalog.models import ProductSize, RegionPrice, Stock
            for size in ProductSize.objects.all():
                RegionPrice.objects.get_or_create(
                    size=size, region=obj, defaults={'price': 0},
                )
                Stock.objects.get_or_create(size=size, region=obj)
