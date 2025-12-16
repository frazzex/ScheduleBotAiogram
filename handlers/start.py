from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html

from keyboards import get_main_keyboard
from utils.user import get_or_create_user

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    """

    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    greeting = f"Привет, {html.bold(message.from_user.full_name)}!\n\n"

    if user.subgroup is None:
        greeting += "Для начала выбери свою подгруппу:"
        await message.answer(greeting, reply_markup=get_main_keyboard())
    else:
        greeting += f"Твоя подгруппа: {user.subgroup}\n\n"
        greeting += "Выбери, что хочешь посмотреть:"
        await message.answer(greeting, reply_markup=get_main_keyboard(user.subgroup))