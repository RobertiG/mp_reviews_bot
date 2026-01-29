import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from app.config import settings

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


async def is_subscribed(user_id: int) -> bool:
    if not settings.telegram_channel_id:
        return False
    member = await bot.get_chat_member(chat_id=settings.telegram_channel_id, user_id=user_id)
    return member.status in {"member", "administrator", "creator"}


@dp.message(CommandStart())
async def start(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")]]
        )
        await message.answer("Подпишись, чтобы пользоваться", reply_markup=keyboard)
        return
    await message.answer("Выберите проект", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.answer("Подписка подтверждена. Выберите проект")
    else:
        await callback.message.answer("Подписка не найдена. Подпишитесь и попробуйте снова")


def main():
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
