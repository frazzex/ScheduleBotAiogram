from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from models import User
from utils.decorators import require_subgroup

from utils.schedule import (
    get_today_lessons_for_user,
    get_user_week_lessons,
    get_general_week_lessons,
)
from utils.formatters import (
    format_today_schedule,
    format_user_week_schedule,
    format_general_week_schedule,
)
from states.settings import SettingsState
from keyboards.reply import get_subgroup_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, user: User, state: FSMContext):
    text = "Привет! Это бот с расписанием 👋\n\n"

    if user.subgroup is None:
        text += 'Сначала выберите свою подгруппу!'
        await state.set_state(SettingsState.choose_subgroup)
        return await message.answer(text, reply_markup=get_subgroup_keyboard())

    text += 'Воспользуйтесь меню для отображения вашего расписания'
    return await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    await state.set_state(SettingsState.choose_subgroup)
    await message.answer("Выберите вашу подгруппу:", reply_markup=get_subgroup_keyboard())


@router.message(F.text == "⚙️ Изменить подгруппу")
async def menu_change_subgroup(message: Message, state: FSMContext):
    await cmd_settings(message, state)


@router.message(SettingsState.choose_subgroup, F.text.in_({"1 подгруппа", "2 подгруппа"}))
async def process_subgroup(message: Message, state: FSMContext, user: User):
    subgroup = 1 if message.text == "1 подгруппа" else 2
    user.subgroup = subgroup
    await user.save()

    await state.clear()
    await message.answer(
        f"Подгруппа сохранена: {subgroup}",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📅 На сегодня")
@require_subgroup
async def menu_today(message: Message, user: User, state: FSMContext):
    lessons = await get_today_lessons_for_user(user)
    text = format_today_schedule(lessons)
    await message.answer(text)


@router.message(F.text == "📚 Моё расписание (чётная)")
@require_subgroup
async def menu_week_even(message: Message, user: User, state: FSMContext):
    lessons = await get_user_week_lessons(user, "even")
    text = format_user_week_schedule(lessons, "even")
    await message.answer(text)


@router.message(F.text == "📚 Моё расписание (нечётная)")
@require_subgroup
async def menu_week_odd(message: Message, user: User, state: FSMContext):
    lessons = await get_user_week_lessons(user, "odd")
    text = format_user_week_schedule(lessons, "odd")
    await message.answer(text)


@router.message(F.text == "📋 Общее (чётная)")
async def menu_general_even(message: Message, user: User):
    lessons = await get_general_week_lessons("even")
    text = format_general_week_schedule(lessons, "even")
    await message.answer(text)


@router.message(F.text == "📋 Общее (нечётная)")
async def menu_general_odd(message: Message, user: User):
    lessons = await get_general_week_lessons("odd")
    text = format_general_week_schedule(lessons, "odd")
    await message.answer(text)


@router.message(Command("today"))
@require_subgroup
async def cmd_today(message: Message, user: User, state: FSMContext):
    await menu_today(message, user)


@router.message(Command("week_even"))
@require_subgroup
async def cmd_week_even(message: Message, user: User, state: FSMContext):
    await menu_week_even(message, user)


@router.message(Command("week_odd"))
@require_subgroup
async def cmd_week_odd(message: Message, user: User, state: FSMContext):
    await menu_week_odd(message, user)


@router.message(Command("general_even"))
async def cmd_general_even(message: Message, user: User):
    await menu_general_even(message, user)


@router.message(Command("general_odd"))
async def cmd_general_odd(message: Message, user: User):
    await menu_general_odd(message, user)
