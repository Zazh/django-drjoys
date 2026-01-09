FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта (исправлено на app)
COPY app /app

# Создание необходимых директорий
RUN mkdir -p /app/media /app/staticfiles

EXPOSE 8009

# Скрипт запуска с проверкой готовности БД
CMD ["sh", "-c", "while ! pg_isready -h db -p 5432 > /dev/null 2>&1; do echo 'Waiting for postgres...'; sleep 1; done && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8009"]