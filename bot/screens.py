from __future__ import annotations

from typing import Iterable, List, Optional

from . import constants
from .types import Button, Screen


def _buttons(rows: Iterable[Iterable[Button]]) -> List[List[Button]]:
    return [list(row) for row in rows]


def subscription_required(channel: str) -> Screen:
    return Screen(
        key=constants.ACTION_SUBSCRIPTION,
        title="Подписка обязательна",
        body=(
            "Чтобы пользоваться ботом, подпишитесь на канал: "
            f"{channel}. После подписки нажмите кнопку ниже."
        ),
        buttons=_buttons([[Button("✅ Проверить подписку", constants.ACTION_CHECK_SUBSCRIPTION)]]),
    )


def start_screen(has_projects: bool) -> Screen:
    buttons: List[List[Button]] = []
    if has_projects:
        buttons.append([Button("📂 Выбрать проект", constants.ACTION_SELECT_PROJECT)])
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
    row: List[Button] = []
    for idx, name in enumerate(projects, start=1):
        row.append(Button(f"{idx}. {name}", constants.ACTION_DASHBOARD))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if is_admin:
        buttons.append(
            [
                Button("➕ Новый проект", constants.ACTION_SELECT_PROJECT),
                Button("⚙️ Настройки", constants.ACTION_PROJECT_SETTINGS),
            ]
        )
    buttons.append([Button("⬅️ Назад", constants.ACTION_START)])
    return Screen(
        key=constants.ACTION_SELECT_PROJECT,
        title="Проекты",
        body="Выберите проект или создайте новый.",
        buttons=buttons,
    )


def dashboard_screen(project_name: Optional[str], is_admin: bool) -> Screen:
    header = project_name or "Без проекта"
    buttons: List[List[Button]] = [
        [
            Button("📝 Лента", constants.ACTION_FEED),
            Button("📚 KB", constants.ACTION_KB_LIST),
        ],
        [Button("📊 Статистика", constants.ACTION_DASHBOARD)],
    ]
    if is_admin:
        buttons.insert(
            1,
            [
                Button("🏪 Кабинеты", constants.ACTION_CABINETS),
                Button("⚙️ Настройки проекта", constants.ACTION_PROJECT_SETTINGS),
            ],
        )
        buttons.append([Button("💳 Баланс", constants.ACTION_BALANCE)])
    buttons.append([Button("⬅️ Проекты", constants.ACTION_SELECT_PROJECT)])
    return Screen(
        key=constants.ACTION_DASHBOARD,
        title=f"Dashboard — {header}",
        body=(
            "Сводка по проекту:\n"
            "• Новые: 12\n"
            "• Без ответа: 5\n"
            "• Эскалации: 1"
        ),
        buttons=_buttons(buttons),
    )


def feed_screen() -> Screen:
    return Screen(
        key=constants.ACTION_FEED,
        title="Лента отзывов и вопросов",
        body=(
            "1) Отзыв • 5★ • SKU-001 • 10.03\n"
            "2) Вопрос • SKU-002 • 09.03\n"
            "3) Отзыв • 2★ • SKU-003 • 09.03"
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
            "Статус: drafted\n"
            "Предложенный ответ: Спасибо за отзыв!\n"
            "Уверенность: 86%"
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
            "2) 10.03 — SKU-001 — Уточнить срок доставки."
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
                [Button("⬅️ Назад", constants.ACTION_DASHBOARD)],
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
                [Button("⬅️ Назад", constants.ACTION_CABINETS)],
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
        buttons=_buttons(
            [
                [Button("Изменить тон", constants.ACTION_PROJECT_SETTINGS)],
                [Button("Настроить автогенерацию", constants.ACTION_PROJECT_SETTINGS)],
                [Button("⬅️ Назад", constants.ACTION_DASHBOARD)],
            ]
        ),
    )


def balance_screen() -> Screen:
    return Screen(
        key=constants.ACTION_BALANCE,
        title="Баланс",
        body="Текущий баланс: 87 токенов.\nИстория списаний: TBD.",
        buttons=_buttons(
            [
                [Button("➕ Пополнить", constants.ACTION_BALANCE)],
                [Button("⬅️ Назад", constants.ACTION_DASHBOARD)],
            ]
        ),
    )
