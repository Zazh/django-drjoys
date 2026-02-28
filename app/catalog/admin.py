from django.contrib import admin

from django.shortcuts import redirect

from .models import (
    Category, Product, ProductSize,
    UnitOfMeasure, Characteristic, ProductCharacteristic,
    ProductMainImage, ProductPackageImage, ProductIndividualImage,
    FAQ, SiteSettings,
)


# ─── Категория ───

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'is_active', 'order'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
    )


# ─── Характеристики ───

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'data_type')


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'order')
    list_editable = ('order',)
    search_fields = ('name',)


# ─── Товар ───

class SizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ('name', 'sku', 'price', 'old_price', 'price_rub', 'old_price_rub', 'in_stock', 'order')


class CharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 1
    fields = ('characteristic', 'value')
    autocomplete_fields = ['characteristic']


class MainImageInline(admin.TabularInline):
    model = ProductMainImage
    extra = 1
    fields = ('image', 'alt_text', 'is_cover', 'order')


class PackageImageInline(admin.TabularInline):
    model = ProductPackageImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


class IndividualImageInline(admin.TabularInline):
    model = ProductIndividualImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'badge', 'is_active')
    list_filter = ('category', 'badge', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category']
    inlines = [SizeInline, CharacteristicInline, MainImageInline, PackageImageInline, IndividualImageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category'),
        }),
        ('Описание', {
            'fields': ('description',),
        }),
        ('Настройки', {
            'fields': ('badge', 'is_active'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description'),
        }),
        ('Zoom (скролл)', {
            'fields': ('zoom_image', 'zoom_rotation_angle'),
        }),
    )


# ─── FAQ ───

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'order')
    list_editable = ('is_active', 'order')


# ─── Настройки сайта ───

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Изображения', {
            'fields': ('placeholder_image',),
            'description': 'Плейсхолдер — изображение-заглушка для товаров без фото.',
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(f'{request.path}{obj.pk}/change/')
