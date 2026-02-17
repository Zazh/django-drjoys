from django.contrib import admin

from .models import (
    Category, Product, ProductImage, ProductSize,
    Characteristic, CharacteristicValue, CategoryCharacteristic,
    ProductCharacteristic, FAQ,
)


# --- Characteristic ---

class CharacteristicValueInline(admin.TabularInline):
    model = CharacteristicValue
    extra = 1
    fields = ('name', 'slug', 'background', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'value_type', 'unit', 'is_multi', 'order')
    list_editable = ('order',)
    list_filter = ('value_type',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CharacteristicValueInline]


# --- Category ---

class CategoryCharacteristicInline(admin.TabularInline):
    model = CategoryCharacteristic
    extra = 1
    fields = ('characteristic', 'is_required', 'display_mode', 'order')
    autocomplete_fields = ['characteristic']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [CategoryCharacteristicInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'is_active', 'order'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
    )


# --- Product ---

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_type', 'alt_text', 'order', 'rotation_angle')


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ('size', 'width_mm', 'length_mm', 'is_available', 'stock_quantity', 'order')


class ProductCharacteristicInline(admin.StackedInline):
    model = ProductCharacteristic
    extra = 0
    fields = ('characteristic', 'value', 'selected_values', 'hint')
    filter_horizontal = ('selected_values',)
    autocomplete_fields = ['characteristic']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'price_rub', 'badge', 'is_active', 'in_stock')
    list_filter = ('category', 'is_active', 'in_stock', 'badge')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('related_products',)
    inlines = [ProductCharacteristicInline, ProductImageInline, ProductSizeInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'category'),
        }),
        ('Цены (₸ тенге)', {
            'fields': ('price', 'old_price'),
        }),
        ('Цены (₽ рубли)', {
            'fields': ('price_rub', 'old_price_rub'),
        }),
        ('Описание', {
            'fields': ('short_description', 'description'),
        }),
        ('Отображение', {
            'fields': ('badge', 'is_active', 'is_featured', 'in_stock'),
        }),
        ('Связанные товары', {
            'fields': ('related_products',),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'order')
    list_editable = ('is_active', 'order')
