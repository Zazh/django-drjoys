from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from catalog.models import (
    Category, Product,
    ProductMainImage, ProductPackageImage, ProductIndividualImage,
)
from catalog.utils import optimize_image_field


class Command(BaseCommand):
    help = 'Конвертирует все существующие изображения каталога в WebP'

    def handle(self, *args, **options):
        total = 0

        # Category.image
        for obj in Category.objects.exclude(image=''):
            result = optimize_image_field(obj.image, max_width=600, quality=80)
            if result:
                obj.image.save(result.name, ContentFile(result.read()), save=False)
                Category.objects.filter(pk=obj.pk).update(image=obj.image)
                total += 1
                self.stdout.write(f'  Category: {obj.name}')

        # Product.zoom_image
        for obj in Product.objects.exclude(zoom_image=''):
            result = optimize_image_field(obj.zoom_image, max_width=1400, quality=85)
            if result:
                obj.zoom_image.save(result.name, ContentFile(result.read()), save=False)
                Product.objects.filter(pk=obj.pk).update(zoom_image=obj.zoom_image)
                total += 1
                self.stdout.write(f'  Zoom: {obj.name}')

        # ProductMainImage — image + thumbnail
        for obj in ProductMainImage.objects.all():
            updated = False
            result = optimize_image_field(obj.image, max_width=800, quality=85)
            if result:
                obj.image.save(result.name, ContentFile(result.read()), save=False)
                updated = True

            thumb = optimize_image_field(obj.image, max_width=600, quality=80)
            if thumb:
                obj.thumbnail.save(thumb.name, ContentFile(thumb.read()), save=False)
                updated = True

            if updated:
                ProductMainImage.objects.filter(pk=obj.pk).update(
                    image=obj.image, thumbnail=obj.thumbnail,
                )
                total += 1
                self.stdout.write(f'  Main: {obj}')

        # ProductPackageImage
        for obj in ProductPackageImage.objects.all():
            result = optimize_image_field(obj.image, max_width=800, quality=82)
            if result:
                obj.image.save(result.name, ContentFile(result.read()), save=False)
                ProductPackageImage.objects.filter(pk=obj.pk).update(image=obj.image)
                total += 1
                self.stdout.write(f'  Package: {obj}')

        # ProductIndividualImage
        for obj in ProductIndividualImage.objects.all():
            result = optimize_image_field(obj.image, max_width=800, quality=82)
            if result:
                obj.image.save(result.name, ContentFile(result.read()), save=False)
                ProductIndividualImage.objects.filter(pk=obj.pk).update(image=obj.image)
                total += 1
                self.stdout.write(f'  Individual: {obj}')

        self.stdout.write(self.style.SUCCESS(f'Оптимизировано: {total} изображений'))
