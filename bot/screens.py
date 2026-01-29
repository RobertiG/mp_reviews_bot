from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from . import constants
from .types import Button, Screen


def _chunk_buttons(buttons: Iterable[Button], columns: int = 2) -> List[List[Button]]:
    rows: List[List[Button]] = []
    row: List[Button] = []
    for button in buttons:
        row.append(button)
        if len(row) == columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def _format_date(value: Optional[str]) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d.%m")
    except ValueError:
        return value


def subscription_required(channel: str, channel_url: Optional[str]) -> Screen:
    buttons = []
    if channel_url:
        buttons.append(Button("Перейти в канал", constants.ACTION_SUBSCRIPTION, url=channel_url))
    buttons.append(Button("Проверить подписку", constants.ACTION_CHECK_SUBSCRIPTION))
    return Screen(
        key=constants.ACTION_SUBSCRIPTION,
        title="Подпишись, чтобы пользоваться",
        body=(
            "Чтобы пользоваться ботом, подпишитесь на канал: "
            f"{channel}. После подписки нажмите кнопку ниже."
        ),
        buttons=_chunk_buttons(buttons),
    )


def start_screen(has_projects: bool) -> Screen:
    buttons: List[Button] = []
    if has_projects:
        buttons.append(Button("Выбрать проект", constants.ACTION_SELECT_PROJECT))
    else:
        buttons.append(Button("➕ Создать проект", constants.ACTION_SELECT_PROJECT))
    return Screen(
        key=constants.ACTION_START,
        title="Добро пожаловать",
        body="Выберите действие, чтобы начать работу с отзывами.",
        buttons=_chunk_buttons(buttons),
    )


def project_selection_screen(projects: Iterable[dict], is_admin: bool) -> Screen:
    project_list = list(projects)
    buttons: List[Button] = []
    for project in project_list:
        buttons.append(Button(project["name"], f"{constants.ACTION_DASHBOARD}:{project['id']}"))
    if is_admin:
        buttons.append(Button("➕ Новый проект", constants.ACTION_SELECT_PROJECT))
        buttons.append(Button("⚙️ Настройки", constants.ACTION_PROJECT_SETTINGS))
    buttons.append(Button("⬅️ Назад", constants.ACTION_BACK))
    return Screen(
        key=constants.ACTION_SELECT_PROJECT,
        title="Проекты",
        body="Выберите проект или создайте новый." if project_list else "Проектов пока нет.",
        buttons=_chunk_buttons(buttons),
    )


def dashboard_screen(project_name: Optional[str], is_admin: bool, dashboard: Optional[dict]) -> Screen:
    header = project_name or "Без проекта"
    buttons: List[Button] = [
        Button("📝 Лента", constants.ACTION_FEED),
        Button("📚 KB", constants.ACTION_KB_LIST),
        Button("📊 Статистика", constants.ACTION_DASHBOARD),
    ]
    if is_admin:
        buttons.append(Button("🏪 Кабинеты", constants.ACTION_CABINETS))
        buttons.append(Button("⚙️ Настройки проекта", constants.ACTION_PROJECT_SETTINGS))
        buttons.append(Button("💳 Баланс", constants.ACTION_BALANCE))
    buttons.append(Button("⬅️ Назад", constants.ACTION_BACK))
    dashboard = dashboard or {}
    return Screen(
        key=constants.ACTION_DASHBOARD,
        title=f"Dashboard — {header}",
        body=(
            "Сводка по проекту:\n"
            f"• Новые: {dashboard.get('new', 0)}\n"
            f"• Без ответа: {dashboard.get('without_answer', 0)}\n"
            f"• Эскалации: {dashboard.get('escalated', 0)}"
            + (
                f"\n• Баланс токенов: {dashboard.get('balance_tokens', 0)}"
                if is_admin
                else ""
            )
        ),
        buttons=_chunk_buttons(buttons),
    )


def feed_screen(events: Iterable[dict], filters: Optional[dict]) -> Screen:
    items = list(events)
    filter_hint = ""
    if filters:
        parts = []
        if filters.get("without_answer"):
            parts.append("статус: без ответа")
        elif filters.get("status"):
            parts.append(f"статус: {filters['status']}")
        if filters.get("sentiment"):
            parts.append(f"тональность: {filters['sentiment']}")
        if filters.get("internal_sku"):
            parts.append(f"SKU: {filters['internal_sku']}")
        if parts:
            filter_hint = "\nФильтр: " + ", ".join(parts)
    if not items:
        body = "Нет событий для выбранных фильтров." + filter_hint
    else:
        lines = []
        for idx, event in enumerate(items, start=1):
            rating = f"{event.get('rating')}★" if event.get("rating") else "—"
            sentiment = event.get("sentiment") or "—"
            lines.append(
                f"{idx}) {event.get('event_type')} • {rating} • {sentiment} • {event.get('internal_sku')} • "
                f"{_format_date(event.get('created_at'))} • {event.get('status')}"
            )
        body = "\n".join(lines) + filter_hint
    buttons: List[Button] = [Button("🔎 Фильтры", constants.ACTION_FEED_FILTERS)]
    for idx, event in enumerate(items, start=1):
        buttons.append(Button(f"Карточка {idx}", f"{constants.ACTION_CARD}:{event['id']}"))
    if filters and filters.get("offset", 0) > 0:
        prev_offset = max(filters.get("offset", 0) - filters.get("limit", 10), 0)
        buttons.append(Button("◀️ Пред", f"{constants.ACTION_FEED}:offset={prev_offset}"))
    if filters and filters.get("has_next"):
        next_offset = filters.get("offset", 0) + filters.get("limit", 10)
        buttons.append(Button("След ▶️", f"{constants.ACTION_FEED}:offset={next_offset}"))
    buttons.append(Button("⬅️ Назад", constants.ACTION_BACK))
    return Screen(
        key=constants.ACTION_FEED,
        title="Лента отзывов и вопросов",
        body=body,
        buttons=_chunk_buttons(buttons),
    )


def feed_filters_screen(filters: Optional[dict]) -> Screen:
    current = []
    if filters:
        if filters.get("without_answer"):
            current.append("статус: без ответа")
        elif filters.get("status"):
            current.append(f"статус: {filters['status']}")
        if filters.get("sentiment"):
            current.append(f"тональность: {filters['sentiment']}")
        if filters.get("internal_sku"):
            current.append(f"SKU: {filters['internal_sku']}")
    note = f"\nТекущие фильтры: {', '.join(current)}" if current else ""
    buttons = [
        Button("Новые", f"{constants.ACTION_FEED}:status=new"),
        Button("Без ответа", f"{constants.ACTION_FEED}:status=without_answer"),
        Button("Answered", f"{constants.ACTION_FEED}:status=sent"),
        Button("Эскалация", f"{constants.ACTION_FEED}:status=escalated"),
        Button("SKU", f"{constants.ACTION_FEED}:sku_prompt"),
        Button("Тональность", f"{constants.ACTION_FEED}:sentiment_prompt"),
        Button("⬅️ Назад", constants.ACTION_BACK),
    ]
    return Screen(
        key=constants.ACTION_FEED_FILTERS,
        title="Фильтры ленты",
        body="Выберите фильтр для ленты:" + note,
        buttons=_chunk_buttons(buttons),
    )


def card_screen(card: Optional[dict]) -> Screen:
    if not card:
        body = "Карточка не выбрана."
    else:
        rating = f"{card.get('rating')}★" if card.get("rating") else "—"
        sentiment = card.get("sentiment") or "—"
        media = card.get("media_links") or []
        media_text = "\n".join(media) if media else "нет"
        kb_sources = card.get("kb_sources") or []
        kb_text = "\n".join(f"• {rule}" for rule in kb_sources) if kb_sources else "нет"
        body = (
            f"Тип: {card.get('event_type')}\n"
            f"Текст: {card.get('text')}\n"
            f"SKU: {card.get('internal_sku')}\n"
            f"Оценка: {rating}\n"
            f"Тональность: {sentiment}\n"
            f"Дата: {_format_date(card.get('created_at'))}\n"
            f"Медиа: {media_text}\n"
            f"Статус: {card.get('status')}\n"
            f"Предложенный ответ: {card.get('suggested_reply') or '—'}\n"
            f"Уверенность: {card.get('confidence') or '—'}%\n"
            f"KB источники:\n{kb_text}"
        )
    buttons = [
        Button("✅ Отправить", constants.ACTION_CARD),
        Button("✏️ Править", constants.ACTION_EDIT),
        Button("♻️ Перегенерировать", constants.ACTION_REGENERATE),
        Button("➕ Добавить правило", constants.ACTION_ADD_KB_RULE),
        Button("🚫 Эскалация", constants.ACTION_CARD),
        Button("⬅️ Назад", constants.ACTION_BACK),
    ]
    return Screen(
        key=constants.ACTION_CARD,
        title="Карточка отзыва",
        body=body,
        buttons=_chunk_buttons(buttons),
    )


def edit_screen(current_reply: Optional[str]) -> Screen:
    return Screen(
        key=constants.ACTION_EDIT,
        title="Правка ответа",
        body=(
            "Текущий ответ:\n"
            f"{current_reply or '—'}\n\n"
            "Отправьте новый текст сообщения, затем нажмите «Сохранить»."
        ),
        buttons=_chunk_buttons(
            [Button("✅ Сохранить", constants.ACTION_CARD), Button("↩️ Отмена", constants.ACTION_BACK)]
        ),
    )


def regenerate_screen() -> Screen:
    return Screen(
        key=constants.ACTION_REGENERATE,
        title="Регенерация ответа",
        body="Генерируем новый ответ...",
        buttons=_chunk_buttons([Button("⬅️ Назад", constants.ACTION_BACK)]),
    )


def add_kb_rule_screen(draft: Optional[dict]) -> Screen:
    draft = draft or {}
    level = draft.get("level") or "не выбран"
    sku = draft.get("internal_sku") or "—"
    text = draft.get("text") or "—"
    body = (
        "Шаг 1/4: уровень (Проект / SKU).\n"
        "Шаг 2/4: выбор SKU (если нужно).\n"
        "Шаг 3/4: текст правила.\n"
        "Шаг 4/4: подтверждение.\n\n"
        f"Уровень: {level}\nSKU: {sku}\nТекст: {text}"
    )
    return Screen(
        key=constants.ACTION_ADD_KB_RULE,
        title="Добавить правило KB",
        body=body,
        buttons=_chunk_buttons(
            [
                Button("Проект", f"{constants.ACTION_ADD_KB_RULE}:level=project"),
                Button("SKU", f"{constants.ACTION_ADD_KB_RULE}:level=sku"),
                Button("✅ Добавить", f"{constants.ACTION_ADD_KB_RULE}:submit"),
                Button("⬅️ Назад", constants.ACTION_BACK),
            ]
        ),
    )


def kb_list_screen(is_admin: bool, rules: Iterable[dict]) -> Screen:
    rules_list = list(rules)
    buttons: List[Button] = [
        Button("Проектные", f"{constants.ACTION_KB_LIST}:scope=project"),
        Button("SKU-правила", f"{constants.ACTION_KB_LIST}:scope=sku"),
    ]
    if is_admin:
        buttons.append(Button("🗑 Удалить", constants.ACTION_KB_DELETE))
    buttons.append(Button("⬅️ Назад", constants.ACTION_BACK))
    if not rules_list:
        body = "Правил пока нет."
    else:
        lines = []
        for idx, rule in enumerate(rules_list, start=1):
            sku = rule.get("internal_sku") or "Проект"
            lines.append(f"{idx}) {_format_date(rule.get('created_at'))} — {sku} — {rule['text']}")
        body = "\n".join(lines)
    return Screen(
        key=constants.ACTION_KB_LIST,
        title="База знаний",
        body=body,
        buttons=_chunk_buttons(buttons),
    )


def kb_delete_screen(rules: Iterable[dict]) -> Screen:
    rules_list = list(rules)
    buttons: List[Button] = []
    for rule in rules_list:
        buttons.append(Button(f"🗑 {rule['id']}", f"{constants.ACTION_KB_DELETE}:{rule['id']}"))
    buttons.append(Button("⬅️ Назад", constants.ACTION_BACK))
    body = "Выберите правило для удаления." if rules_list else "Нет правил для удаления."
    return Screen(
        key=constants.ACTION_KB_DELETE,
        title="Удаление правила",
        body=body,
        buttons=_chunk_buttons(buttons),
    )


def cabinets_screen(cabinets: Iterable[dict]) -> Screen:
    cabinets_list = list(cabinets)
    body = (
        "Подключённые кабинеты:\n"
        + "\n".join(
            f"• {cabinet['marketplace']} — {cabinet['name']}" for cabinet in cabinets_list
        )
        if cabinets_list
        else "Кабинеты не подключены."
    )
    buttons = [
        Button("➕ Добавить кабинет", constants.ACTION_ONBOARDING),
        Button("🔄 Проверить подключение", constants.ACTION_CABINETS),
        Button("🗑 Удалить кабинет", constants.ACTION_CABINETS),
        Button("⬅️ Назад", constants.ACTION_BACK),
    ]
    return Screen(
        key=constants.ACTION_CABINETS,
        title="Кабинеты маркетплейсов",
        body=body,
        buttons=_chunk_buttons(buttons),
    )


def onboarding_screen(onboarding: Optional[dict]) -> Screen:
    onboarding = onboarding or {}
    if onboarding.get("has_cabinets"):
        body = "Онбординг завершён. Кабинеты подключены."
    else:
        body = "Кабинеты не подключены. Начните онбординг."
    return Screen(
        key=constants.ACTION_ONBOARDING,
        title="Онбординг кабинета",
        body=body,
        buttons=_chunk_buttons(
            [
                Button("WB", f"{constants.ACTION_ONBOARDING}:marketplace=WB"),
                Button("Ozon", f"{constants.ACTION_ONBOARDING}:marketplace=OZON"),
                Button("⬅️ Назад", constants.ACTION_BACK),
            ]
        ),
    )


def project_settings_screen(settings: Optional[dict]) -> Screen:
    settings = settings or {}
    return Screen(
        key=constants.ACTION_PROJECT_SETTINGS,
        title="Настройки проекта",
        body=(
            "Тон бренда: не задан.\n"
            f"Автогенерация 5/4★: {'включена' if settings.get('autogen_positive') else 'выключена'}\n"
            f"Автоотправка 5/4★: {'включена' if settings.get('autosend_positive') else 'выключена'}\n"
            f"Автогенерация 1–3★: {'включена' if settings.get('autogen_negative') else 'выключена'}\n"
            f"Автоотправка 1–3★: {'включена' if settings.get('autosend_negative') else 'выключена'}\n"
            f"Автогенерация вопросы: {'включена' if settings.get('autogen_questions') else 'выключена'}\n"
            f"Автоотправка вопросы: {'включена' if settings.get('autosend_questions') else 'выключена'}"
        ),
        buttons=_chunk_buttons([Button("⬅️ Назад", constants.ACTION_BACK)]),
    )


def balance_screen(balance: Optional[dict]) -> Screen:
    balance = balance or {}
    ledger = balance.get("ledger") or []
    if ledger:
        history = "\n".join(
            f"• {_format_date(item.get('created_at'))}: {item.get('delta')} ({item.get('reason')})"
            for item in ledger
        )
    else:
        history = "Нет операций."
    return Screen(
        key=constants.ACTION_BALANCE,
        title="Баланс",
        body=(
            f"Текущий баланс: {balance.get('tokens', 0)} токенов.\n"
            f"История списаний:\n{history}"
        ),
        buttons=_chunk_buttons(
            [Button("➕ Пополнить", constants.ACTION_BALANCE), Button("⬅️ Назад", constants.ACTION_BACK)]
        ),
    )
