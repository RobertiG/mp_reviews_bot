# mp_reviews_bot

MVP сервиса Telegram-бота для автоответов на отзывы/вопросы Wildberries и Ozon.

## Быстрый старт

```bash
cp .env.example .env
docker-compose up --build
```

API будет доступен на `http://localhost:8000`, health-check `GET /health`.

## Конфигурация (.env)

- `DATABASE_URL`
- `REDIS_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`
- `ENCRYPTION_KEY`

## Принятые решения

- Очередь задач: Celery + Redis (дефолт из ТЗ).
- LLM: абстрактный адаптер без привязки к провайдеру (дефолт из ТЗ).
- XLSX хранится только в памяти и удаляется после обработки (дефолт из ТЗ).
- Уверенность ИИ: integer 0–100 (дефолт из ТЗ).
- Язык интерфейса: RU (дефолт из ТЗ).
- Для событий без явного признака изменения сохраняется новая запись, чтобы не терять данные.

## Структура

- `app/` — FastAPI backend
- `bot/` — Telegram bot
- `worker/` — Celery задачи
- `migrations/` — Alembic миграции

## Миграции

```bash
alembic upgrade head
```

## Тесты

```bash
pytest
```
