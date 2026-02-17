import json

from django.db.models import Prefetch
from django.http import Http404
from django.views.generic import ListView, DetailView

from .models import (
    Category, Product, ProductImage, ProductCharacteristic,
    CategoryCharacteristic, FAQ,
)


class CatalogListView(ListView):
    model = Product
    template_name = 'pages/catalog.html'
    context_object_name = 'products'

    def get_queryset(self):
        qs = (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('images')
        )
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            qs = qs.filter(category__slug=category_slug, category__is_active=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        categories = Category.objects.filter(is_active=True)
        category_slug = self.kwargs.get('category_slug')
        current_category = None
        if category_slug:
            try:
                current_category = categories.get(slug=category_slug)
            except Category.DoesNotExist:
                raise Http404
        ctx['categories'] = categories
        ctx['current_category'] = current_category
        ctx['faqs'] = FAQ.objects.filter(is_active=True)
        ctx['page_type'] = 'catalog'
        ctx['meta_title'] = (
            current_category.meta_title or current_category.name
            if current_category
            else 'Каталог презервативов DR.JOYS'
        )
        ctx['meta_description'] = (
            current_category.meta_description
            if current_category
            else 'Каталог презервативов DR.JOYS — классические, ребристые, ультратонкие'
        )
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related(
                'images',
                'sizes',
                Prefetch(
                    'characteristics',
                    queryset=ProductCharacteristic.objects
                    .select_related('characteristic')
                    .prefetch_related('selected_values'),
                ),
                'related_products__images',
                'related_products__category',
            )
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.category.slug != self.kwargs['category_slug']:
            raise Http404
        return obj

    def _build_characteristics(self, product):
        """Собирает характеристики в готовые для шаблона dict'ы."""
        # display_mode из CategoryCharacteristic
        display_modes = dict(
            CategoryCharacteristic.objects
            .filter(category=product.category)
            .values_list('characteristic_id', 'display_mode')
        )
        result = []
        for pc in product.characteristics.all():
            display = pc.display_value
            if not display:
                continue
            result.append({
                'name': pc.characteristic.name,
                'value': display,
                'hint': pc.hint,
                'inline': display_modes.get(pc.characteristic_id) == 'inline',
            })
        return result

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        images = product.images.all()

        ctx['main_image'] = images.filter(image_type=ProductImage.ImageType.MAIN).first()
        ctx['gallery_images'] = images.filter(image_type=ProductImage.ImageType.GALLERY)
        ctx['zoom_image'] = images.filter(image_type=ProductImage.ImageType.ZOOM).first()
        ctx['slider_package_images'] = images.filter(image_type=ProductImage.ImageType.SLIDER_PKG)
        ctx['slider_individual_images'] = images.filter(image_type=ProductImage.ImageType.SLIDER_IND)
        ctx['sizes'] = product.sizes.all()
        ctx['related_products'] = product.related_products.filter(is_active=True)[:6]
        ctx['product_characteristics'] = self._build_characteristics(product)
        ctx['page_type'] = 'product_detail'

        # Хлебные крошки
        breadcrumbs = [
            {'name': 'DR.JOYS', 'url': '/'},
            {'name': 'Каталог', 'url': '/catalog/'},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.name, 'url': ''},
        ]
        ctx['breadcrumbs'] = breadcrumbs

        # JSON-LD для хлебных крошек
        jsonld = {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [],
        }
        for i, crumb in enumerate(breadcrumbs, 1):
            item = {
                '@type': 'ListItem',
                'position': i,
                'name': crumb['name'],
            }
            if crumb['url']:
                item['item'] = self.request.build_absolute_uri(crumb['url'])
            jsonld['itemListElement'].append(item)
        ctx['breadcrumb_jsonld'] = json.dumps(jsonld, ensure_ascii=False)

        ctx['meta_title'] = product.meta_title or product.name
        ctx['meta_description'] = product.meta_description or product.short_description
        return ctx
