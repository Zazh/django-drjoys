import io
from pathlib import Path

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def optimize_image_field(image_field, max_width, quality=82):
    """
    Конвертирует ImageField в WebP, ресайзит до max_width (сохраняя пропорции).
    Возвращает InMemoryUploadedFile или None если обработка не нужна.
    """
    if not image_field:
        return None

    image_field.file.seek(0)
    img = Image.open(image_field.file)

    # Уже WebP и меньше max_width — пропускаем
    if img.format == 'WEBP' and img.width <= max_width:
        image_field.file.seek(0)
        return None

    # Конвертируем в RGB
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Ресайз только если больше max_width
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Сохраняем в буфер как WebP
    buffer = io.BytesIO()
    img.save(buffer, format='WEBP', quality=quality, method=4)
    size = buffer.tell()
    buffer.seek(0)

    # Новое имя с .webp
    original_name = Path(image_field.name).stem
    new_name = f'{original_name}.webp'

    image_field.file.seek(0)

    return InMemoryUploadedFile(
        file=buffer,
        field_name=None,
        name=new_name,
        content_type='image/webp',
        size=size,
        charset=None,
    )
