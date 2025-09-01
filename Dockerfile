# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /code

# Системные зависимости (для psycopg/psycopg2)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Сначала зависимости — лучше кэшируется
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# (Опционально) non-root пользователь
# RUN useradd -m appuser
# USER appuser

# Код проекта
COPY . .

# CMD задаём в docker-compose
