from django.http import Http404
from django.views.generic import ListView, DetailView

from .models import Category, Product, FAQ
from . import jsonld as jld


class CatalogListView(ListView):
    model = Product
    template_name = 'pages/catalog.html'
    context_object_name = 'products'

    def get_queryset(self):
        qs = (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('main_images', 'sizes')
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
        faqs = FAQ.objects.filter(is_active=True)
        ctx['faqs'] = faqs
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

        # JSON-LD
        breadcrumbs = [
            {'name': 'DR.JOYS', 'url': '/'},
            {'name': 'Каталог', 'url': '/catalog/'},
        ]
        if current_category:
            breadcrumbs.append({
                'name': current_category.name,
                'url': current_category.get_absolute_url(),
            })
        ctx['jsonld_blocks'] = jld.serialize_jsonld(
            jld.build_breadcrumb_jsonld(self.request, breadcrumbs),
            jld.build_catalog_itemlist_jsonld(self.request, ctx['products'], current_category),
            jld.build_faq_jsonld(faqs),
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
                'sizes',
                'characteristics__characteristic__unit',
                'main_images',
                'package_images',
                'individual_images',
            )
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.category.slug != self.kwargs['category_slug']:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object

        sizes = list(product.sizes.all())
        ctx['sizes'] = sizes
        ctx['default_size'] = sizes[0] if sizes else None
        cover_image = product.main_images.filter(is_cover=True).first()
        ctx['cover_image'] = cover_image
        main_images = list(product.main_images.all())
        ctx['main_images'] = main_images
        ctx['package_images'] = product.package_images.all()
        ctx['individual_images'] = product.individual_images.all()
        characteristics = list(
            product.characteristics.select_related('characteristic__unit').all()
        )
        ctx['characteristics'] = characteristics
        ctx['page_type'] = 'product_detail'

        # Хлебные крошки
        breadcrumbs = [
            {'name': 'DR.JOYS', 'url': '/'},
            {'name': 'Каталог', 'url': '/catalog/'},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.name, 'url': ''},
        ]
        ctx['breadcrumbs'] = breadcrumbs

        # JSON-LD
        ctx['jsonld_blocks'] = jld.serialize_jsonld(
            jld.build_breadcrumb_jsonld(self.request, breadcrumbs),
            jld.build_product_jsonld(
                self.request, product, sizes, cover_image, main_images, characteristics,
            ),
        )

        ctx['meta_title'] = product.meta_title or product.name
        ctx['meta_description'] = product.meta_description or product.description
        return ctx
