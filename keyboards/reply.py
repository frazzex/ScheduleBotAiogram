from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_subgroup_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 подгруппа"), KeyboardButton(text="2 подгруппа")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите подгруппу"
    )


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 На сегодня")],
            [KeyboardButton(text="📚 Моё расписание (чётная)"), KeyboardButton(text="📚 Моё расписание (нечётная)")],
            [KeyboardButton(text="📋 Общее (чётная)"), KeyboardButton(text="📋 Общее (нечётная)")],
            [KeyboardButton(text="⚙️ Изменить подгруппу")]
        ],
        resize_keyboard=True
    )
