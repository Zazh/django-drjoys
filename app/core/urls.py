from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

# Без языкового префикса
urlpatterns = [
    path('admin/', admin.site.urls),
    path('region/', include('regions.urls')),
]

# С языковым префиксом (/ru/, /kk/, /en/)
urlpatterns += i18n_patterns(
    path('catalog/', include('catalog.urls')),
    path('', TemplateView.as_view(template_name='pages/home.html', extra_context={'page_type': 'home'}), name='home'),
    path('', include('pages.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
