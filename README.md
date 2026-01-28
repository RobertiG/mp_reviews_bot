# mp_reviews_bot

## Audit logging

The audit log table is defined in `mp_reviews_bot.models.AuditLog` and captures sender, prompt/model/version,
KB rule references, raw payload, and processing status. Use `mp_reviews_bot.audit.record_audit_log` to persist
entries when responses are generated or sent.

Structured logging can be enabled via `mp_reviews_bot.logging.setup_structured_logging()` to emit JSON log lines
with optional audit metadata under the `audit` key.

## Retention

Celery task `audit.purge_old_logs` deletes audit log entries older than 90 days (configurable via
`AUDIT_RETENTION_DAYS`) and is scheduled daily at 03:00 UTC via Celery beat (override with
`CELERY_TIMEZONE`).
Бот часть проекта Проще - его задача обрабатывать и отвечать на отзывы пользователей.

## Минимальный доменный слой (MVP)

В репозитории добавлены базовые модели баланса/ledger и политика обработки событий.
Их можно использовать в сервисном слое при интеграции с БД и очередью задач.

### Основные сущности

- `OwnerAccount` — владелец с текущим балансом токенов и политикой обработки после пополнения.
- `LedgerEntry` — запись о движении токенов (списание, пополнение).
- `BillingService` — сервис списания и пополнения токенов у owner.
- `EventProcessingPolicy` — блокирует парсинг/генерацию при нулевом балансе и задаёт окно после пополнения.

### Поведение при нулевом балансе

- Любая генерация и парсинг новых событий блокируются.
- После пополнения выбирается политика: обработать накопленные события или только новые.

### Выбор поведения после пополнения

`BillingService.top_up` принимает `policy`, а `EventProcessingPolicy.window_after_replenishment`
возвращает окно обработки:

- `PROCESS_BACKLOG` — `include_backlog=True`, стартовая отметка не ограничена.
- `ONLY_NEW` — обработка только новых событий, начиная с времени пополнения.
## XLSX импорт SKU

Модуль `mp_reviews_bot.xlsx_importer` отвечает за загрузку и разбор XLSX-шаблонов для сопоставления SKU. Он проверяет:

- строгий формат колонок (`SKU_MAPPING` + заголовки по ТЗ);
- ограничение размера файла;
- антифлуд по ключу загрузки;
- таймаут обработки.

Для применения результатов предусмотрен список `rebinds`, который отражает перепривязку `seller_sku` к новому `internal_sku`, чтобы история событий отображалась под новым `internal_sku`.

Бот часть проекта Проще — его задача обрабатывать и отвечать на отзывы пользователей.

## Запуск

1. Создайте файл `.env` в корне (см. список переменных ниже).
2. Соберите и поднимите сервисы:

```bash
docker compose up -d --build
```

3. Примените миграции (когда они будут добавлены):

```bash
docker compose run --rm app <команда_миграций>
```

## Переменные окружения

Минимальный набор для локального запуска:

- `TG_BOT_TOKEN` — токен Telegram-бота.
- `DATABASE_URL` — строка подключения к PostgreSQL.
- `REDIS_URL` — строка подключения к Redis (очередь задач).
- `LLM_PROVIDER` — имя провайдера LLM (например, `openai`, `anthropic`, `mock`).
- `LLM_MODEL` — идентификатор модели LLM.

Дополнительные (опционально):

- `LOG_LEVEL` — уровень логирования (например, `INFO`).
- `WEBHOOK_BASE_URL` — базовый URL для Telegram webhook (если используется webhook).

## Архитектура

- `app/` — HTTP/API сервис (управление проектами, кабинетами, KB, настройками и т.д.).
- `bot/` — Telegram-бот (UI, навигация, команды, подтверждения действий).
- `worker/` — воркеры очереди (генерация ответов, парсинг, автоотправка, обработка медиа).
- `migrations/` — миграции базы данных.
- `docker-compose.yml` — оркестрация сервисов локально.

Сервисные зависимости:

- PostgreSQL — основная БД.
- Redis — брокер очереди задач.

## Принятые решения

### Дефолты из секции «Проверка полноты ТЗ для Codex»

- Очередь задач: **Celery + Redis**.
- Модель ИИ: **абстрактный LLM-провайдер через адаптер**.
- Хранение XLSX: **временное хранение + удаление после обработки**.
- Уверенность ИИ: **integer 0–100**.
- Язык интерфейса: **RU**.

### Дополнительные безопасные решения

- Основная БД — PostgreSQL 16 (дефолт для локального окружения).
- Redis 7 как брокер для фоновых задач.
- Хранение секретов — только через переменные окружения (без коммита в репозиторий).
- Все сервисы в локальной разработке поднимаются через `docker compose`.
