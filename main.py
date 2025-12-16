import asyncio
import logging
import sys
from os import getenv
import dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from database import init_db, close_db

from utils.user import get_or_create_user
from utils.common import is_even_week_from_september
from utils.schedule import get_general_schedule, get_schedule_for_user
from keyboards import get_main_keyboard
from handlers import start

# Bot token can be obtained via https://t.me/BotFather
dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

dp.include_routers(start.router)

@dp.message(Command("subgroup"))
async def command_subgroup_handler(message: Message) -> None:
    """Обработчик команды выбора подгруппы"""
    await message.answer(
        "Выбери свою подгруппу:",
        reply_markup=get_main_keyboard()
    )


@dp.callback_query(F.data.startswith("subgroup_"))
async def callback_subgroup_handler(callback: CallbackQuery) -> None:
    """Обработчик выбора подгруппы через кнопку"""
    subgroup_num = int(callback.data.split("_")[1])

    user = await get_or_create_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    user.subgroup = subgroup_num
    await user.save()

    await callback.message.edit_text(
        f"Отлично! Твоя подгруппа: {subgroup_num}\n\n"
        "Выбери, что хочешь посмотреть:",
        reply_markup=get_main_keyboard(subgroup_num)
    )
    await callback.answer()


@dp.callback_query(F.data == "change_subgroup")
async def callback_change_subgroup_handler(callback: CallbackQuery) -> None:
    """Обработчик изменения подгруппы"""
    await callback.message.edit_text(
        "Выбери свою подгруппу:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@dp.message(Command("schedule"))
async def command_schedule_handler(message: Message) -> None:
    """Обработчик команды просмотра расписания"""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    if user.subgroup is None:
        await message.answer(
            "Сначала выбери свою подгруппу:",
            reply_markup=get_main_keyboard()
        )
        return

    week_type = "even" if is_even_week_from_september() else "odd"
    schedule_text = await get_schedule_for_user(user, week_type)
    await message.answer(schedule_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))


@dp.callback_query(F.data == "schedule_current")
async def callback_schedule_current_handler(callback: CallbackQuery) -> None:
    """Обработчик просмотра расписания на текущую неделю"""
    user = await get_or_create_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    if user.subgroup is None:
        await callback.answer("Сначала выбери подгруппу!", show_alert=True)
        return

    week_type = "even" if is_even_week_from_september() else "odd"
    schedule_text = await get_schedule_for_user(user, week_type)

    # Разбиваем длинное сообщение на части, если нужно
    if len(schedule_text) > 4096:
        parts = [schedule_text[i:i + 4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN,
                                         reply_markup=get_main_keyboard(user.subgroup))

    await callback.answer()


@dp.callback_query(F.data == "schedule_next")
async def callback_schedule_next_handler(callback: CallbackQuery) -> None:
    """Обработчик просмотра расписания на следующую неделю"""
    user = await get_or_create_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    if user.subgroup is None:
        await callback.answer("Сначала выбери подгруппу!", show_alert=True)
        return

    # Следующая неделя - противоположный тип
    current_week_type = "even" if is_even_week_from_september() else "odd"
    next_week_type = "odd" if current_week_type == "even" else "even"

    schedule_text = await get_schedule_for_user(user, next_week_type)

    if len(schedule_text) > 4096:
        parts = [schedule_text[i:i + 4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN,
                                         reply_markup=get_main_keyboard(user.subgroup))

    await callback.answer()


@dp.callback_query(F.data == "schedule_general_current")
async def callback_schedule_general_current_handler(callback: CallbackQuery) -> None:
    """Обработчик просмотра общего расписания на текущую неделю"""
    week_type = "even" if is_even_week_from_september() else "odd"
    schedule_text = await get_general_schedule(week_type)

    user = await get_or_create_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    if len(schedule_text) > 4096:
        parts = [schedule_text[i:i + 4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN,
                                         reply_markup=get_main_keyboard(user.subgroup))

    await callback.answer()


@dp.callback_query(F.data == "schedule_general_next")
async def callback_schedule_general_next_handler(callback: CallbackQuery) -> None:
    """Обработчик просмотра общего расписания на следующую неделю"""
    current_week_type = "even" if is_even_week_from_september() else "odd"
    next_week_type = "odd" if current_week_type == "even" else "even"

    schedule_text = await get_general_schedule(next_week_type)

    user = await get_or_create_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    if len(schedule_text) > 4096:
        parts = [schedule_text[i:i + 4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN,
                                         reply_markup=get_main_keyboard(user.subgroup))

    await callback.answer()


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Обработчик всех остальных сообщений
    """
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    await message.answer(
        "Используй команды:\n"
        "/start - начать работу\n"
        "/subgroup - выбрать подгруппу\n"
        "/schedule - посмотреть расписание\n\n"
        "Или используй кнопки ниже:",
        reply_markup=get_main_keyboard(user.subgroup)
    )


async def main() -> None:
    # Инициализация базы данных
    await init_db()

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        # And the run events dispatching
        await dp.start_polling(bot)
    finally:
        # Закрываем подключение к БД при завершении
        await close_db()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
