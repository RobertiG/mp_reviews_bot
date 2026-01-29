from __future__ import annotations

from typing import Iterable, List, Optional

from . import constants
from .types import Button, Screen


def _buttons(rows: Iterable[Iterable[Button]]) -> List[List[Button]]:
    return [list(row) for row in rows]


def subscription_required(channel: str) -> Screen:
    return Screen(
        key=constants.ACTION_SUBSCRIPTION,
        title="Подпишись, чтобы пользоваться",
        body=(
            "Чтобы пользоваться ботом, подпишитесь на канал: "
            f"{channel}. После подписки нажмите кнопку ниже."
        ),
        buttons=_buttons([[Button("Проверить подписку", constants.ACTION_CHECK_SUBSCRIPTION)]]),
        keyboard="inline",
    )


def start_screen(has_projects: bool) -> Screen:
    buttons: List[List[Button]] = []
    if has_projects:
        buttons.append([Button("Выбрать проект", constants.ACTION_SELECT_PROJECT)])
    else:
        buttons.append([Button("➕ Создать проект", constants.ACTION_SELECT_PROJECT)])
    return Screen(
        key=constants.ACTION_START,
        title="Добро пожаловать",
        body="Выберите действие, чтобы начать работу с отзывами.",
        buttons=buttons,
    )


def project_selection_screen(projects: Iterable[str], is_admin: bool) -> Screen:
    buttons: List[List[Button]] = []
    for name in projects:
        buttons.append([Button(name, constants.ACTION_DASHBOARD)])
    if is_admin:
        buttons.append(
            [
                Button("➕ Новый проект", constants.ACTION_SELECT_PROJECT),
                Button("⚙️ Настройки", constants.ACTION_PROJECT_SETTINGS),
            ]
        )
    return Screen(
        key=constants.ACTION_SELECT_PROJECT,
        title="Проекты",
        body="Выберите проект или создайте новый.",
        buttons=buttons,
    )


def dashboard_screen(project_name: Optional[str], is_admin: bool) -> Screen:
    header = project_name or "Без проекта"
    buttons: List[List[Button]] = [
        [Button("📝 Лента", constants.ACTION_FEED)],
        [Button("📚 KB", constants.ACTION_KB_LIST)],
        [Button("📊 Статистика", constants.ACTION_DASHBOARD)],
    ]
    if is_admin:
        buttons.insert(2, [Button("🏪 Кабинеты", constants.ACTION_CABINETS)])
        buttons.insert(3, [Button("⚙️ Настройки проекта", constants.ACTION_PROJECT_SETTINGS)])
        buttons.append([Button("💳 Баланс", constants.ACTION_BALANCE)])
    return Screen(
        key=constants.ACTION_DASHBOARD,
        title=f"Dashboard — {header}",
        body=(
            "Сводка по проекту:\n"
            "• Новые: 12\n"
            "• Без ответа: 5\n"
            "• Эскалации: 1"
            + ("\n• Баланс токенов: 87" if is_admin else "")
        ),
        buttons=_buttons(buttons),
    )


def feed_screen() -> Screen:
    return Screen(
        key=constants.ACTION_FEED,
        title="Лента отзывов и вопросов",
        body=(
            "1) Отзыв • 5★ • SKU-001 • 10.03 • drafted\n"
            "2) Вопрос • нейтр. • SKU-002 • 10.03 • new\n"
            "3) Отзыв • 2★ • SKU-003 • 09.03 • escalated\n"
            "4) Отзыв • 4★ • SKU-004 • 09.03 • approved\n"
            "5) Вопрос • позитив • SKU-005 • 09.03 • drafted\n"
            "6) Отзыв • 1★ • SKU-006 • 08.03 • new\n"
            "7) Отзыв • 3★ • SKU-007 • 08.03 • sent\n"
            "8) Вопрос • нейтр. • SKU-008 • 08.03 • drafted\n"
            "9) Отзыв • 5★ • SKU-009 • 07.03 • approved\n"
            "10) Отзыв • 4★ • SKU-010 • 07.03 • error"
        ),
        buttons=_buttons(
            [
                [Button("🔎 Фильтры", constants.ACTION_FEED_FILTERS)],
                [Button("◀️ Пред", constants.ACTION_FEED), Button("След ▶️", constants.ACTION_FEED)],
                [Button("⬅️ Назад", constants.ACTION_DASHBOARD)],
            ]
        ),
    )


def feed_filters_screen() -> Screen:
    return Screen(
        key=constants.ACTION_FEED_FILTERS,
        title="Фильтры ленты",
        body="Выберите фильтр для ленты:",
        buttons=_buttons(
            [
                [Button("Новые", constants.ACTION_FEED), Button("Без ответа", constants.ACTION_FEED)],
                [Button("Answered", constants.ACTION_FEED), Button("Эскалация", constants.ACTION_FEED)],
                [Button("SKU", constants.ACTION_FEED), Button("Тональность", constants.ACTION_FEED)],
                [Button("⬅️ Назад", constants.ACTION_FEED)],
            ]
        ),
        keyboard="inline",
    )


def card_screen() -> Screen:
    return Screen(
        key=constants.ACTION_CARD,
        title="Карточка отзыва",
        body=(
            "Тип: Отзыв\n"
            "Текст: Отличное качество, спасибо!\n"
            "SKU: SKU-001 (WB: 12345, Ozon: 98765)\n"
            "Оценка: 5★\n"
            "Тональность: позитив\n"
            "Дата: 10.03\n"
            "Медиа: https://example.com/photo1\n"
            "Статус: drafted\n"
            "Предложенный ответ: Спасибо за отзыв!\n"
            "Уверенность: 86%\n"
            "KB источники:\n"
            "• Всегда благодарим за отзыв\n"
            "• Уточнить срок доставки"
        ),
        buttons=_buttons(
            [
                [Button("✅ Отправить", constants.ACTION_CARD), Button("✏️ Править", constants.ACTION_EDIT)],
                [
                    Button("♻️ Перегенерировать", constants.ACTION_REGENERATE),
                    Button("➕ Добавить правило", constants.ACTION_ADD_KB_RULE),
                ],
                [Button("🚫 Эскалация", constants.ACTION_CARD)],
                [Button("⬅️ Назад в ленту", constants.ACTION_FEED)],
            ]
        ),
    )


def edit_screen() -> Screen:
    return Screen(
        key=constants.ACTION_EDIT,
        title="Правка ответа",
        body=(
            "Текущий ответ:\n"
            "Спасибо за ваш отзыв!\n\n"
            "Отправьте новый текст сообщения, затем нажмите «Сохранить»."
        ),
        buttons=_buttons(
            [[Button("✅ Сохранить", constants.ACTION_CARD), Button("↩️ Отмена", constants.ACTION_CARD)]]
        ),
        keyboard="inline",
    )


def regenerate_screen() -> Screen:
    return Screen(
        key=constants.ACTION_REGENERATE,
        title="Регенерация ответа",
        body="Генерируем новый ответ...",
        buttons=_buttons([[Button("⬅️ Назад в карточку", constants.ACTION_CARD)]]),
        keyboard="inline",
    )


def add_kb_rule_screen() -> Screen:
    return Screen(
        key=constants.ACTION_ADD_KB_RULE,
        title="Добавить правило KB",
        body=(
            "Шаг 1/4: уровень (Проект / SKU).\n"
            "Шаг 2/4: выбор SKU (если нужно).\n"
            "Шаг 3/4: текст правила.\n"
            "Шаг 4/4: подтверждение."
        ),
        buttons=_buttons(
            [
                [Button("Проект", constants.ACTION_ADD_KB_RULE), Button("SKU", constants.ACTION_ADD_KB_RULE)],
                [Button("✅ Добавить", constants.ACTION_KB_LIST)],
                [Button("⬅️ Назад", constants.ACTION_CARD)],
            ]
        ),
        keyboard="inline",
    )


def kb_list_screen(is_admin: bool) -> Screen:
    buttons: List[List[Button]] = [
        [Button("Проектные", constants.ACTION_KB_LIST), Button("SKU-правила", constants.ACTION_KB_LIST)],
    ]
    if is_admin:
        buttons.append([Button("🗑 Удалить", constants.ACTION_KB_DELETE)])
    buttons.append([Button("⬅️ Назад", constants.ACTION_DASHBOARD)])
    return Screen(
        key=constants.ACTION_KB_LIST,
        title="База знаний",
        body=(
            "1) 12.03 — Проект — Всегда благодарим за отзыв.\n"
            "2) 11.03 — Проект — Используем дружелюбный тон.\n"
            "3) 11.03 — SKU-001 — Уточнить срок доставки.\n"
            "4) 10.03 — SKU-002 — Благодарим за покупку.\n"
            "5) 10.03 — SKU-003 — Извиняемся и предлагаем замену.\n"
            "6) 09.03 — Проект — Не упоминать скидки.\n"
            "7) 09.03 — SKU-004 — Сообщаем о гарантии.\n"
            "8) 08.03 — SKU-005 — Просим фото дефекта.\n"
            "9) 08.03 — Проект — Благодарим за обратную связь.\n"
            "10) 07.03 — SKU-006 — Уточняем комплектацию."
        ),
        buttons=_buttons(buttons),
    )


def kb_delete_screen() -> Screen:
    return Screen(
        key=constants.ACTION_KB_DELETE,
        title="Удаление правила",
        body="Выберите правило для удаления или вернитесь назад.",
        buttons=_buttons(
            [
                [Button("🗑 1", constants.ACTION_KB_DELETE), Button("🗑 2", constants.ACTION_KB_DELETE)],
                [Button("🗑 3", constants.ACTION_KB_DELETE), Button("🗑 4", constants.ACTION_KB_DELETE)],
                [Button("⬅️ Назад", constants.ACTION_KB_LIST)],
            ]
        ),
        keyboard="inline",
    )


def cabinets_screen() -> Screen:
    return Screen(
        key=constants.ACTION_CABINETS,
        title="Кабинеты маркетплейсов",
        body="Подключённые кабинеты: WB-1, Ozon-1.",
        buttons=_buttons(
            [
                [Button("➕ Добавить кабинет", constants.ACTION_ONBOARDING)],
                [Button("🔄 Проверить подключение", constants.ACTION_CABINETS)],
                [Button("🗑 Удалить кабинет", constants.ACTION_CABINETS)],
            ]
        ),
    )


def onboarding_screen() -> Screen:
    return Screen(
        key=constants.ACTION_ONBOARDING,
        title="Онбординг кабинета",
        body=(
            "Шаг 1/4: выберите маркетплейс (WB/Ozon).\n"
            "Шаг 2/4: введите токен.\n"
            "Шаг 3/4: тест подключения.\n"
            "Шаг 4/4: подтверждение."
        ),
        buttons=_buttons(
            [
                [Button("WB", constants.ACTION_ONBOARDING), Button("Ozon", constants.ACTION_ONBOARDING)],
            ]
        ),
        keyboard="inline",
    )


def project_settings_screen() -> Screen:
    return Screen(
        key=constants.ACTION_PROJECT_SETTINGS,
        title="Настройки проекта",
        body=(
            "Тон бренда: дружелюбный, экспертный.\n"
            "Автогенерация 5/4★: включена\n"
            "Автогенерация 1–3★: включена\n"
            "Автогенерация вопросы: включена"
        ),
        buttons=[],
    )


def balance_screen() -> Screen:
    return Screen(
        key=constants.ACTION_BALANCE,
        title="Баланс",
        body="Текущий баланс: 87 токенов.\nИстория списаний: TBD.",
        buttons=_buttons(
            [
                [Button("➕ Пополнить", constants.ACTION_BALANCE)],
            ]
        ),
    )
