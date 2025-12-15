from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
            InlineKeyboardButton(text="Показать расписание на сегодня", callback_data="show_today_schedule")
        ])
        keyboard.append([
            InlineKeyboardButton(text="⚙️ Изменить подгруппу", callback_data="change_subgroup")
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)