from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Страницы для верстки
    path('', TemplateView.as_view(template_name='pages/home.html', extra_context={'page_type': 'home'}), name='home'),
    path('catalog/', TemplateView.as_view(template_name='pages/catalog.html', extra_context={'page_type': 'catalog'}), name='catalog'),
    path('product/', TemplateView.as_view(template_name='pages/product_detail.html', extra_context={'page_type': 'product_detail'}), name='product_detail'),
    path('blog/', TemplateView.as_view(template_name='pages/blog_list.html', extra_context={'page_type': 'blog_list'}), name='blog_list'),
    path('blog/detail/', TemplateView.as_view(template_name='pages/blog_detail.html', extra_context={'page_type': 'blog_detail'}), name='blog_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])