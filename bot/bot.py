import asyncio
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
    await state.update_data(current_action=result.screen.key)
    next_state = ACTION_STATE_MAP.get(result.screen.key)
    if next_state:
        await state.set_state(next_state)


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    await route_action(constants.ACTION_START, message, state)


@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
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
            await state.update_data(kb_rule_text=message.text)
            await message.answer("Текст правила сохранён. Нажмите «✅ Добавить».")
            return
        return
    await route_action(
        action,
        message,
        state,
        payload_text=message.text,
        current_action=current_action,
    )


def main() -> None:
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
