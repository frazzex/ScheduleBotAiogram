from models import User
from models import Lesson
from .common import time_to_minutes

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

