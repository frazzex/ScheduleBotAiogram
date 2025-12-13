import asyncio
import logging
import sys
from os import getenv
import dotenv
from datetime import datetime
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models import User, Subject, Lesson
from database import init_db, close_db

# Bot token can be obtained via https://t.me/BotFather
dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


def is_even_week_from_september() -> bool:
    today = datetime.now().date()
    september_start = datetime(today.year, 9, 1).date()
    if today < september_start:
        september_start = datetime(today.year - 1, 9, 1).date()
    days_since_september = (today - september_start).days

    week_number = days_since_september // 7 + 1

    return week_number % 2 == 0





async def get_or_create_user(user_id: int, username: str = None, full_name: str = None) -> User:
    """Получить или создать пользователя"""
    user, created = await User.get_or_create(
        id=user_id,
        defaults={
            'username': username,
            'full_name': full_name
        }
    )
    if not created:
        # Обновляем данные, если они изменились
        if username and user.username != username:
            user.username = username
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        await user.save()
    return user


def time_to_minutes(time_str: str) -> int:
    """Преобразует время в формате 'HH:MM' в минуты с начала дня"""
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    except (ValueError, AttributeError):
        return 0


async def get_schedule_for_user(user: User, week_type: str, show_all: bool = False) -> str:
    """Получить расписание для пользователя с учетом его подгруппы
    
    Args:
        user: Пользователь
        week_type: Тип недели ("even" или "odd")
        show_all: Если True, показывать все пары (общее расписание), иначе только для подгруппы пользователя
    """
    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    week_label = "ЧЁТНАЯ НЕДЕЛЯ" if week_type == "even" else "НЕЧЁТНАЯ НЕДЕЛЯ"
    schedule_text = f"**{week_label}**\n\n"
    
    # Получаем все пары для данной недели
    lessons_query = Lesson.filter(
        week_type__in=[week_type, None]  # Пары для данной недели или для обеих
    ).prefetch_related('subject').order_by('day_of_week', 'start_time')
    
    lessons = await lessons_query
    
    if not lessons:
        return schedule_text + "Расписание пока не заполнено в базе данных."
    
    # Фильтруем по подгруппе и сортируем по времени
    filtered_lessons = []
    for lesson in lessons:
        # Фильтруем по подгруппе, если не показываем все
        if not show_all:
            if lesson.subgroup is not None and user.subgroup is not None:
                if lesson.subgroup != user.subgroup:
                    continue
        filtered_lessons.append(lesson)
    
    # Сортируем по дню недели и времени начала
    filtered_lessons.sort(key=lambda l: (l.day_of_week, time_to_minutes(l.start_time)))
    
    current_day = -1
    has_lessons = False
    
    for lesson in filtered_lessons:
        # Фильтруем по подгруппе, если не показываем все
        if not show_all:
            if lesson.subgroup is not None and user.subgroup is not None:
                if lesson.subgroup != user.subgroup:
                    continue
        
        has_lessons = True
        
        # Если день изменился, добавляем заголовок дня
        if lesson.day_of_week != current_day:
            if current_day != -1:
                schedule_text += "\n"
            schedule_text += f"**{day_names[lesson.day_of_week]}:**\n"
            current_day = lesson.day_of_week
        
        # Формируем строку пары
        lesson_str = f"- {lesson.start_time}–{lesson.end_time} — «{lesson.subject.name}» ({lesson.lesson_type})"
        if lesson.teacher:
            lesson_str += f", {lesson.teacher}"
        if lesson.classroom:
            lesson_str += f", ауд. {lesson.classroom}"
        if lesson.subgroup:
            lesson_str += f" ({lesson.subgroup} подгруппа)"
        lesson_str += ";\n"
        
        schedule_text += lesson_str
    
    if not has_lessons:
        return schedule_text + "Нет пар для твоей подгруппы на этой неделе."
    
    return schedule_text


async def get_general_schedule(week_type: str) -> str:
    """Получить общее расписание для всех подгрупп"""
    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    week_label = "ЧЁТНАЯ НЕДЕЛЯ" if week_type == "even" else "НЕЧЁТНАЯ НЕДЕЛЯ"
    schedule_text = f"**{week_label}**\n\n"
    
    # Получаем все пары для данной недели
    lessons = await Lesson.filter(
        week_type__in=[week_type, None]
    ).prefetch_related('subject').order_by('day_of_week', 'start_time')
    
    if not lessons:
        return schedule_text + "Расписание пока не заполнено в базе данных."
    
    # Сортируем по дню недели и времени начала
    lessons_list = list(lessons)
    lessons_list.sort(key=lambda l: (l.day_of_week, time_to_minutes(l.start_time)))
    
    current_day = -1
    for lesson in lessons_list:
        # Если день изменился, добавляем заголовок дня
        if lesson.day_of_week != current_day:
            if current_day != -1:
                schedule_text += "\n"
            schedule_text += f"**{day_names[lesson.day_of_week]}:**\n"
            current_day = lesson.day_of_week
        
        # Формируем строку пары
        lesson_str = f"- {lesson.start_time}–{lesson.end_time} — «{lesson.subject.name}» ({lesson.lesson_type})"
        if lesson.teacher:
            lesson_str += f", {lesson.teacher}"
        if lesson.classroom:
            lesson_str += f", ауд. {lesson.classroom}"
        if lesson.subgroup:
            lesson_str += f" ({lesson.subgroup} подгруппа)"
        lesson_str += ";\n"
        
        schedule_text += lesson_str
    
    return schedule_text


def get_main_keyboard(user_subgroup: int = None) -> InlineKeyboardMarkup:
    """Создает главную клавиатуру с кнопками"""
    keyboard = []
    
    if user_subgroup is None:
        # Если подгруппа не выбрана, показываем кнопки для выбора
        keyboard.append([
            InlineKeyboardButton(text="1 подгруппа", callback_data="subgroup_1"),
            InlineKeyboardButton(text="2 подгруппа", callback_data="subgroup_2")
        ])
    else:
        # Если подгруппа выбрана, показываем кнопки расписания
        keyboard.append([
            InlineKeyboardButton(text="📅 Текущая неделя", callback_data="schedule_current"),
            InlineKeyboardButton(text="📅 Следующая неделя", callback_data="schedule_next")
        ])
        keyboard.append([
            InlineKeyboardButton(text="📋 Общее расписание (текущая)", callback_data="schedule_general_current"),
            InlineKeyboardButton(text="📋 Общее расписание (следующая)", callback_data="schedule_general_next")
        ])
        keyboard.append([
            InlineKeyboardButton(text="⚙️ Изменить подгруппу", callback_data="change_subgroup")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@dp.message(CommandStart())
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
        parts = [schedule_text[i:i+4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
    
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
        parts = [schedule_text[i:i+4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
    
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
        parts = [schedule_text[i:i+4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
    
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
        parts = [schedule_text[i:i+4096] for i in range(0, len(schedule_text), 4096)]
        for i, part in enumerate(parts):
            if i == 0:
                await callback.message.edit_text(part, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
            else:
                await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.edit_text(schedule_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.subgroup))
    
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