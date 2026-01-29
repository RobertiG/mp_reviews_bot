import asyncio
from typing import Iterable, Optional, Tuple

import httpx
from typing import Iterable, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from bot import constants, navigation, screens, subscription
from bot.types import BotDependencies, Screen, UserContext

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher(storage=MemoryStorage())

DEFAULT_PROJECTS = [f"Проект {idx}" for idx in range(1, 11)]

class ScreenStates(StatesGroup):
    subscription = State()
    start = State()
    select_project = State()
    dashboard = State()
    feed = State()
    feed_filters = State()
    card = State()
    edit = State()
    regenerate = State()
    add_kb_rule = State()
    kb_list = State()
    kb_delete = State()
    cabinets = State()
    onboarding = State()
    project_settings = State()
    balance = State()

class ScreenStates(StatesGroup):
    subscription = State()
    start = State()
    select_project = State()
    dashboard = State()
    feed = State()
    feed_filters = State()
    card = State()
    edit = State()
    regenerate = State()
    add_kb_rule = State()
    kb_list = State()
    kb_delete = State()
    cabinets = State()
    onboarding = State()
    project_settings = State()
    balance = State()


ACTION_STATE_MAP = {
    constants.ACTION_SUBSCRIPTION: ScreenStates.subscription,
    constants.ACTION_START: ScreenStates.start,
    constants.ACTION_SELECT_PROJECT: ScreenStates.select_project,
    constants.ACTION_DASHBOARD: ScreenStates.dashboard,
    constants.ACTION_FEED: ScreenStates.feed,
    constants.ACTION_FEED_FILTERS: ScreenStates.feed_filters,
    constants.ACTION_CARD: ScreenStates.card,
    constants.ACTION_EDIT: ScreenStates.edit,
    constants.ACTION_REGENERATE: ScreenStates.regenerate,
    constants.ACTION_ADD_KB_RULE: ScreenStates.add_kb_rule,
    constants.ACTION_KB_LIST: ScreenStates.kb_list,
    constants.ACTION_KB_DELETE: ScreenStates.kb_delete,
    constants.ACTION_CABINETS: ScreenStates.cabinets,
    constants.ACTION_ONBOARDING: ScreenStates.onboarding,
    constants.ACTION_PROJECT_SETTINGS: ScreenStates.project_settings,
    constants.ACTION_BALANCE: ScreenStates.balance,
}


def _keyboard_rows(buttons: Iterable[Iterable[types.InlineKeyboardButton]]):
    return list(buttons)

ACTION_STATE_MAP = {
    constants.ACTION_SUBSCRIPTION: ScreenStates.subscription,
    constants.ACTION_START: ScreenStates.start,
    constants.ACTION_SELECT_PROJECT: ScreenStates.select_project,
    constants.ACTION_DASHBOARD: ScreenStates.dashboard,
    constants.ACTION_FEED: ScreenStates.feed,
    constants.ACTION_FEED_FILTERS: ScreenStates.feed_filters,
    constants.ACTION_CARD: ScreenStates.card,
    constants.ACTION_EDIT: ScreenStates.edit,
    constants.ACTION_REGENERATE: ScreenStates.regenerate,
    constants.ACTION_ADD_KB_RULE: ScreenStates.add_kb_rule,
    constants.ACTION_KB_LIST: ScreenStates.kb_list,
    constants.ACTION_KB_DELETE: ScreenStates.kb_delete,
    constants.ACTION_CABINETS: ScreenStates.cabinets,
    constants.ACTION_ONBOARDING: ScreenStates.onboarding,
    constants.ACTION_PROJECT_SETTINGS: ScreenStates.project_settings,
    constants.ACTION_BALANCE: ScreenStates.balance,
}


def _keyboard_rows(buttons: Iterable[Iterable[types.InlineKeyboardButton]]):
    return list(buttons)


def build_keyboard(screen: Screen) -> Optional[types.InlineKeyboardMarkup]:
    if not screen.buttons:
        return None
    inline_rows = []
    for row in screen.buttons:
        inline_row = []
        for btn in row:
            if btn.url:
                inline_row.append(types.InlineKeyboardButton(text=btn.text, url=btn.url))
            else:
                inline_row.append(types.InlineKeyboardButton(text=btn.text, callback_data=btn.action))
        inline_rows.append(inline_row)
    return types.InlineKeyboardMarkup(inline_keyboard=_keyboard_rows(inline_rows))


def format_screen_text(screen: Screen) -> str:
    if screen.body:
        return f"{screen.title}\n\n{screen.body}"
    return screen.title


async def send_screen(target: types.Message | types.CallbackQuery, screen: Screen) -> None:
    text = format_screen_text(screen)
    reply_markup = build_keyboard(screen)
    if isinstance(target, types.CallbackQuery):
        await target.message.answer(text, reply_markup=reply_markup)
        await target.answer()
    else:
        await target.answer(text, reply_markup=reply_markup)


class BotAPI:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def _get(self, path: str, params: Optional[dict] = None) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()

    async def _delete(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.delete(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def profile(self, tg_user_id: int) -> dict:
        return await self._get(f"/bot/profile/{tg_user_id}")

    async def projects(self, tg_user_id: int) -> list[dict]:
        return await self._get(f"/bot/projects/{tg_user_id}")

    async def dashboard(self, tg_user_id: int, project_id: int) -> dict:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/dashboard")

    async def feed(self, tg_user_id: int, project_id: int, params: dict) -> dict:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/feed", params=params)

    async def event(self, tg_user_id: int, event_id: int) -> dict:
        return await self._get(f"/bot/events/{tg_user_id}/{event_id}")

    async def kb_rules(self, tg_user_id: int, project_id: int, params: dict) -> list[dict]:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/kb", params=params)

    async def delete_kb_rule(self, tg_user_id: int, rule_id: int) -> dict:
        return await self._delete(f"/bot/kb/{tg_user_id}/{rule_id}")

    async def create_kb_rule(self, tg_user_id: int, project_id: int, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/bot/projects/{tg_user_id}/{project_id}/kb",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def cabinets(self, tg_user_id: int, project_id: int) -> list[dict]:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/cabinets")

    async def onboarding(self, tg_user_id: int, project_id: int) -> dict:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/onboarding")

    async def settings(self, tg_user_id: int, project_id: int) -> dict:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/settings")

    async def balance(self, tg_user_id: int, project_id: int) -> dict:
        return await self._get(f"/bot/projects/{tg_user_id}/{project_id}/balance")


actions_with_history = {
    constants.ACTION_START,
    constants.ACTION_SELECT_PROJECT,
    constants.ACTION_DASHBOARD,
    constants.ACTION_FEED,
    constants.ACTION_FEED_FILTERS,
    constants.ACTION_CARD,
    constants.ACTION_EDIT,
    constants.ACTION_REGENERATE,
    constants.ACTION_ADD_KB_RULE,
    constants.ACTION_KB_LIST,
    constants.ACTION_KB_DELETE,
    constants.ACTION_CABINETS,
    constants.ACTION_ONBOARDING,
    constants.ACTION_PROJECT_SETTINGS,
    constants.ACTION_BALANCE,
}


def parse_callback(data: str) -> Tuple[str, Optional[str]]:
    if ":" in data:
        action, payload = data.split(":", 1)
        return action, payload
    return data, None


def action_from_text(screen: Screen, text: str) -> Optional[str]:
    for row in screen.buttons:
        for btn in row:
            if btn.text == text:
                return btn.action
    return None


async def refresh_subscription(
    user_id: int, state: FSMContext, channel_id: str, force: bool = False
) -> bool:
    data = await state.get_data()
    if data.get("has_subscription") and not force:
        return True
    status = await asyncio.to_thread(
        subscription.get_chat_member,
        settings.telegram_bot_token,
        channel_id,
        user_id,
    )
    has_subscription = subscription.is_subscribed(status)
    await state.update_data(has_subscription=has_subscription)
    return has_subscription


async def build_context(
    action: str,
    user_id: int,
    state: FSMContext,
    api: BotAPI,
    payload: Optional[str] = None,
) -> UserContext:
    data = await state.get_data()
    profile = await api.profile(user_id)
    current_project_id = data.get("current_project_id")
    current_project_name = data.get("current_project_name")
    projects = data.get("projects") or await api.projects(user_id)
    if "projects" not in data:
        await state.update_data(projects=projects)
    if current_project_id and not current_project_name:
        project = next((item for item in projects if item["id"] == current_project_id), None)
        if project:
            current_project_name = project["name"]
            await state.update_data(current_project_name=current_project_name)
    ctx = UserContext(
        user_id=user_id,
        is_admin=profile.get("is_admin", False),
        has_subscription=data.get("has_subscription"),
        current_project_id=current_project_id,
        current_project_name=current_project_name,
        projects=projects,
        feed_filters=data.get("feed_filters"),
        edit_draft=data.get("draft_reply"),
        kb_rule_draft=data.get("kb_rule_draft"),
    )

    if action in {constants.ACTION_DASHBOARD} and current_project_id:
        ctx.dashboard = await api.dashboard(user_id, current_project_id)
    if action in {constants.ACTION_FEED, constants.ACTION_FEED_FILTERS} and current_project_id:
        filters = data.get("feed_filters") or {"limit": 10, "offset": 0}
        feed = await api.feed(user_id, current_project_id, filters)
        ctx.feed = feed.get("items", [])
        ctx.feed_filters = {
            **filters,
            "total": feed.get("total", 0),
            "limit": feed.get("limit", filters.get("limit", 10)),
            "offset": feed.get("offset", filters.get("offset", 0)),
            "has_next": (feed.get("offset", 0) + feed.get("limit", 10)) < feed.get("total", 0),
        }
    if action in {constants.ACTION_CARD, constants.ACTION_EDIT, constants.ACTION_REGENERATE}:
        event_id = data.get("current_event_id")
        if payload and payload.isdigit():
            event_id = int(payload)
            await state.update_data(current_event_id=event_id)
        if event_id:
            ctx.card = await api.event(user_id, event_id)
    if action in {constants.ACTION_KB_LIST, constants.ACTION_KB_DELETE} and current_project_id:
        kb_filters = data.get("kb_filters") or {"limit": 10}
        ctx.kb_rules = await api.kb_rules(user_id, current_project_id, kb_filters)
    if action == constants.ACTION_CABINETS and current_project_id:
        ctx.cabinets = await api.cabinets(user_id, current_project_id)
    if action == constants.ACTION_ONBOARDING and current_project_id:
        ctx.onboarding = await api.onboarding(user_id, current_project_id)
    if action == constants.ACTION_PROJECT_SETTINGS and current_project_id:
        ctx.settings = await api.settings(user_id, current_project_id)
    if action == constants.ACTION_BALANCE and current_project_id:
        ctx.balance = await api.balance(user_id, current_project_id)

    return ctx


async def handle_back(state: FSMContext) -> Tuple[str, Optional[str]]:
    data = await state.get_data()
    stack = data.get("nav_stack", [])
    if stack:
        last = stack.pop()
        await state.update_data(nav_stack=stack)
        return last.get("action", constants.ACTION_DASHBOARD), last.get("payload")
    if data.get("current_project_id"):
        return constants.ACTION_DASHBOARD, None
    return constants.ACTION_SELECT_PROJECT, None


async def update_nav_stack(state: FSMContext, current_action: Optional[str], payload: Optional[str]) -> None:
    if not current_action or current_action not in actions_with_history:
        return
    data = await state.get_data()
    stack = data.get("nav_stack", [])
    stack.append({"action": current_action, "payload": payload})
    await state.update_data(nav_stack=stack)


async def route_action(
    action: str,
    target: types.Message | types.CallbackQuery,
    state: FSMContext,
    payload: Optional[str] = None,
    current_action: Optional[str] = None,
) -> None:
    channel_id = settings.telegram_channel_id or constants.DEFAULT_REQUIRED_CHANNEL
    channel_url = settings.telegram_channel_url or settings.tg_channel_url
    if channel_id:
        force_check = action == constants.ACTION_CHECK_SUBSCRIPTION
        try:
            subscribed = await refresh_subscription(
                target.from_user.id, state, channel_id, force=force_check
            )
        except RuntimeError as exc:
            await target.answer(str(exc))
            await send_screen(target, screens.subscription_required(channel_id, channel_url))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if not subscribed:
            if action == constants.ACTION_CHECK_SUBSCRIPTION:
                await target.answer("Подписка не найдена. Подпишитесь и попробуйте снова.")
            await send_screen(target, screens.subscription_required(channel_id, channel_url))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if action == constants.ACTION_CHECK_SUBSCRIPTION:
            data = await state.get_data()
            if data.get("current_project_id"):
                action = constants.ACTION_DASHBOARD
            else:
                action = constants.ACTION_SELECT_PROJECT

    if action == constants.ACTION_BACK:
        action, payload = await handle_back(state)
    else:
        data = await state.get_data()
        await update_nav_stack(state, current_action, data.get("current_payload"))

    api = BotAPI(settings.api_base_url)

    if action == constants.ACTION_DASHBOARD and payload and payload.isdigit():
        project_id = int(payload)
        projects = await api.projects(target.from_user.id)
        project = next((item for item in projects if item["id"] == project_id), None)
        await state.update_data(
            current_project_id=project_id,
            current_project_name=project["name"] if project else None,
            projects=projects,
        )

    if action == constants.ACTION_FEED and payload:
        data = await state.get_data()
        filters = data.get("feed_filters", {"limit": 10, "offset": 0})
        if payload.startswith("offset="):
            filters["offset"] = int(payload.split("=", 1)[1])
        elif payload.startswith("status="):
            status = payload.split("=", 1)[1]
            filters = {"limit": 10, "offset": 0}
            if status == "without_answer":
                filters["without_answer"] = True
            else:
                filters["status"] = status
        elif payload == "sku_prompt":
            await state.update_data(pending_filter="sku")
            await target.answer("Введите SKU для фильтрации.")
            return
        elif payload == "sentiment_prompt":
            await state.update_data(pending_filter="sentiment")
            await target.answer("Введите тональность (позитив/нейтр/негатив).")
            return
        await state.update_data(feed_filters=filters, pending_filter=None)

    if action == constants.ACTION_KB_LIST and payload:
        scope = payload.split("=", 1)[1] if "=" in payload else None
        kb_filters = {"limit": 10}
        if scope == "project":
            kb_filters["scope"] = "project"
        elif scope == "sku":
            kb_filters["scope"] = "sku"
        await state.update_data(kb_filters=kb_filters)

    if action == constants.ACTION_KB_DELETE and payload and payload.isdigit():
        await api.delete_kb_rule(target.from_user.id, int(payload))

    if action == constants.ACTION_ADD_KB_RULE and payload:
        data = await state.get_data()
        draft = data.get("kb_rule_draft", {})
        if payload.startswith("level="):
            draft["level"] = payload.split("=", 1)[1]
            if draft["level"] == "sku":
                await state.update_data(kb_rule_draft=draft, pending_kb_sku=True)
                await target.answer("Введите SKU для правила.")
                return
            draft.pop("internal_sku", None)
        elif payload == "submit":
            project_id = data.get("current_project_id")
            if not project_id:
                await target.answer("Сначала выберите проект.")
                return
            text = draft.get("text")
            if not text:
                await target.answer("Добавьте текст правила перед сохранением.")
                return
            await api.create_kb_rule(
                target.from_user.id,
                project_id,
                {
                    "project_id": project_id,
                    "internal_sku": draft.get("internal_sku"),
                    "text": text,
                },
            )
            await state.update_data(kb_rule_draft={}, pending_kb_sku=None)
            action = constants.ACTION_KB_LIST
        await state.update_data(kb_rule_draft=draft)

    try:
        ctx = await build_context(action, target.from_user.id, state, api, payload=payload)
    except httpx.HTTPError as exc:
        await target.answer(f"Ошибка загрузки данных: {exc}")
        return

def build_keyboard(screen: Screen) -> Optional[types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup | types.ReplyKeyboardRemove]:
    if not screen.buttons:
        return types.ReplyKeyboardRemove()
    if screen.keyboard == "inline":
        inline_rows = [
            [types.InlineKeyboardButton(text=btn.text, callback_data=btn.action) for btn in row]
            for row in screen.buttons
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=_keyboard_rows(inline_rows))
    reply_rows = [[types.KeyboardButton(text=btn.text) for btn in row] for row in screen.buttons]
    return types.ReplyKeyboardMarkup(keyboard=reply_rows, resize_keyboard=True)

async def route_action(
    action: str,
    target: types.Message | types.CallbackQuery,
    state: FSMContext,
    payload: Optional[str] = None,
    current_action: Optional[str] = None,
) -> None:
    channel_id = settings.telegram_channel_id or constants.DEFAULT_REQUIRED_CHANNEL
    channel_url = settings.telegram_channel_url or settings.tg_channel_url
    if channel_id:
        force_check = action == constants.ACTION_CHECK_SUBSCRIPTION
        try:
            subscribed = await refresh_subscription(
                target.from_user.id, state, channel_id, force=force_check
            )
        except RuntimeError as exc:
            await target.answer(str(exc))
            await send_screen(target, screens.subscription_required(channel_id, channel_url))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if not subscribed:
            if action == constants.ACTION_CHECK_SUBSCRIPTION:
                await target.answer("Подписка не найдена. Подпишитесь и попробуйте снова.")
            await send_screen(target, screens.subscription_required(channel_id, channel_url))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if action == constants.ACTION_CHECK_SUBSCRIPTION:
            data = await state.get_data()
            if data.get("current_project_id"):
                action = constants.ACTION_DASHBOARD
            else:
                action = constants.ACTION_SELECT_PROJECT

    if action == constants.ACTION_BACK:
        action, payload = await handle_back(state)
    else:
        data = await state.get_data()
        await update_nav_stack(state, current_action, data.get("current_payload"))

    api = BotAPI(settings.api_base_url)

    if action == constants.ACTION_DASHBOARD and payload and payload.isdigit():
        project_id = int(payload)
        projects = await api.projects(target.from_user.id)
        project = next((item for item in projects if item["id"] == project_id), None)
        await state.update_data(
            current_project_id=project_id,
            current_project_name=project["name"] if project else None,
            projects=projects,
        )

    if action == constants.ACTION_FEED and payload:
        data = await state.get_data()
        filters = data.get("feed_filters", {"limit": 10, "offset": 0})
        if payload.startswith("offset="):
            filters["offset"] = int(payload.split("=", 1)[1])
        elif payload.startswith("status="):
            status = payload.split("=", 1)[1]
            filters = {"limit": 10, "offset": 0}
            if status == "without_answer":
                filters["without_answer"] = True
            else:
                filters["status"] = status
        elif payload == "sku_prompt":
            await state.update_data(pending_filter="sku")
            await target.answer("Введите SKU для фильтрации.")
            return
        elif payload == "sentiment_prompt":
            await state.update_data(pending_filter="sentiment")
            await target.answer("Введите тональность (позитив/нейтр/негатив).")
            return
        await state.update_data(feed_filters=filters, pending_filter=None)

    if action == constants.ACTION_KB_LIST and payload:
        scope = payload.split("=", 1)[1] if "=" in payload else None
        kb_filters = {"limit": 10}
        if scope == "project":
            kb_filters["scope"] = "project"
        elif scope == "sku":
            kb_filters["scope"] = "sku"
        await state.update_data(kb_filters=kb_filters)

    if action == constants.ACTION_KB_DELETE and payload and payload.isdigit():
        await api.delete_kb_rule(target.from_user.id, int(payload))

    if action == constants.ACTION_ADD_KB_RULE and payload:
        data = await state.get_data()
        draft = data.get("kb_rule_draft", {})
        if payload.startswith("level="):
            draft["level"] = payload.split("=", 1)[1]
            if draft["level"] == "sku":
                await state.update_data(kb_rule_draft=draft, pending_kb_sku=True)
                await target.answer("Введите SKU для правила.")
                return
            draft.pop("internal_sku", None)
        elif payload == "submit":
            project_id = data.get("current_project_id")
            if not project_id:
                await target.answer("Сначала выберите проект.")
                return
            text = draft.get("text")
            if not text:
                await target.answer("Добавьте текст правила перед сохранением.")
                return
            await api.create_kb_rule(
                target.from_user.id,
                project_id,
                {
                    "project_id": project_id,
                    "internal_sku": draft.get("internal_sku"),
                    "text": text,
                },
            )
            await state.update_data(kb_rule_draft={}, pending_kb_sku=None)
            action = constants.ACTION_KB_LIST
        await state.update_data(kb_rule_draft=draft)

    try:
        ctx = await build_context(action, target.from_user.id, state, api, payload=payload)
    except httpx.HTTPError as exc:
        await target.answer(f"Ошибка загрузки данных: {exc}")
        return
def format_screen_text(screen: Screen) -> str:
    if screen.body:
        return f"{screen.title}\n\n{screen.body}"
    return screen.title


async def send_screen(target: types.Message | types.CallbackQuery, screen: Screen) -> None:
    text = format_screen_text(screen)
    reply_markup = build_keyboard(screen)
    if isinstance(target, types.CallbackQuery):
        await target.message.answer(text, reply_markup=reply_markup)
        await target.answer()
    else:
        await target.answer(text, reply_markup=reply_markup)


async def build_context(user_id: int, state: FSMContext) -> UserContext:
    data = await state.get_data()
    projects = data.get("projects") or DEFAULT_PROJECTS
    if "projects" not in data:
        await state.update_data(projects=projects)
    is_admin = data.get("is_admin", True)
    current_project = data.get("current_project")
    has_subscription = data.get("has_subscription")
    return UserContext(
        user_id=user_id,
        is_admin=is_admin,
        has_subscription=has_subscription,
        current_project=current_project,
        projects=projects,
    )


def action_from_text(screen: Screen, text: str) -> Optional[str]:
    for row in screen.buttons:
        for btn in row:
            if btn.text == text:
                return btn.action
    return None


async def refresh_subscription(
    user_id: int, state: FSMContext, channel_id: str, force: bool = False
) -> bool:
    data = await state.get_data()
    if data.get("has_subscription") and not force:
        return True
    status = await asyncio.to_thread(
        subscription.get_chat_member,
        settings.telegram_bot_token,
        channel_id,
        user_id,
    )
    has_subscription = subscription.is_subscribed(status)
    await state.update_data(has_subscription=has_subscription)
    return has_subscription


async def route_action(
    action: str,
    target: types.Message | types.CallbackQuery,
    state: FSMContext,
    payload_text: Optional[str] = None,
    current_action: Optional[str] = None,
) -> None:
    channel_id = settings.telegram_channel_id or constants.DEFAULT_REQUIRED_CHANNEL
    if channel_id:
        force_check = action == constants.ACTION_CHECK_SUBSCRIPTION
        try:
            subscribed = await refresh_subscription(
                target.from_user.id, state, channel_id, force=force_check
            )
        except RuntimeError as exc:
            await target.answer(str(exc))
            await send_screen(target, screens.subscription_required(channel_id))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if not subscribed:
            await send_screen(target, screens.subscription_required(channel_id))
            await state.set_state(ScreenStates.subscription)
            await state.update_data(current_action=constants.ACTION_SUBSCRIPTION)
            return
        if action == constants.ACTION_CHECK_SUBSCRIPTION:
            action = constants.ACTION_START

    if action == constants.ACTION_DASHBOARD and current_action == constants.ACTION_SELECT_PROJECT:
        if payload_text:
            await state.update_data(current_project=payload_text)

    ctx = await build_context(target.from_user.id, state)
    deps = BotDependencies(
        bot_token="",
        required_channel="",
        get_chat_member=lambda *_: "",
    )
    result = navigation.handle_action(action, ctx, deps)
    for notice in result.notices:
        await target.answer(notice)
    await send_screen(target, result.screen)
    await state.update_data(current_action=result.screen.key, current_payload=payload)
    await state.update_data(current_action=result.screen.key)
    next_state = ACTION_STATE_MAP.get(result.screen.key)
    if next_state:
        await state.set_state(next_state)


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    await route_action(constants.ACTION_START, message, state)


@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    action, payload = parse_callback(callback.data or constants.ACTION_START)
    data = await state.get_data()
    current_action = data.get("current_action")
    await route_action(action, callback, state, payload=payload, current_action=current_action)
    action = callback.data or constants.ACTION_START
    data = await state.get_data()
    current_action = data.get("current_action")
    await route_action(action, callback, state, current_action=current_action)


@dp.message()
async def handle_message(message: types.Message, state: FSMContext) -> None:
    channel_id = settings.telegram_channel_id or constants.DEFAULT_REQUIRED_CHANNEL
    if channel_id:
        data = await state.get_data()
        if not data.get("has_subscription"):
            await route_action(constants.ACTION_CHECK_SUBSCRIPTION, message, state)
            return

    data = await state.get_data()
    pending_filter = data.get("pending_filter")
    pending_kb_sku = data.get("pending_kb_sku")
    if pending_filter == "sku":
        filters = data.get("feed_filters", {"limit": 10, "offset": 0})
        filters["internal_sku"] = message.text
        await state.update_data(feed_filters=filters, pending_filter=None)
        await route_action(constants.ACTION_FEED, message, state)
        return
    if pending_filter == "sentiment":
        filters = data.get("feed_filters", {"limit": 10, "offset": 0})
        filters["sentiment"] = message.text
        await state.update_data(feed_filters=filters, pending_filter=None)
        await route_action(constants.ACTION_FEED, message, state)
        return
    if pending_kb_sku:
        draft = data.get("kb_rule_draft", {})
        draft["internal_sku"] = message.text
        await state.update_data(kb_rule_draft=draft, pending_kb_sku=None)
        await route_action(constants.ACTION_ADD_KB_RULE, message, state)
        return

    current_action = data.get("current_action", constants.ACTION_START)
    api = BotAPI(settings.api_base_url)
    try:
        ctx = await build_context(current_action, message.from_user.id, state, api)
    except httpx.HTTPError as exc:
        await message.answer(f"Ошибка загрузки данных: {exc}")
        return
    data = await state.get_data()
    current_action = data.get("current_action", constants.ACTION_START)
    ctx = await build_context(message.from_user.id, state)
    deps = BotDependencies(
        bot_token="",
        required_channel="",
        get_chat_member=lambda *_: "",
    )
    screen = navigation.handle_action(current_action, ctx, deps).screen
    action = action_from_text(screen, message.text or "")
    if not action:
        if current_action == constants.ACTION_EDIT:
            await state.update_data(draft_reply=message.text)
            await message.answer("Черновик обновлён. Нажмите «✅ Сохранить» или «↩️ Отмена».")
            return
        if current_action == constants.ACTION_ADD_KB_RULE:
            draft = data.get("kb_rule_draft", {})
            draft["text"] = message.text
            await state.update_data(kb_rule_draft=draft)
            await state.update_data(kb_rule_text=message.text)
            await message.answer("Текст правила сохранён. Нажмите «✅ Добавить».")
            return
        return
    await route_action(
        action,
        message,
        state,
        payload=None,
        payload_text=message.text,
        current_action=current_action,
    )


def main() -> None:
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
