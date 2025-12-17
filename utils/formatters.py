from itertools import groupby
from typing import Sequence
from datetime import date

from models import Lesson


def format_today_schedule(lessons: Sequence[Lesson]) -> str:
    today = date.today()
    today_str = today.strftime('%d.%m.%Y')

    if not lessons:
        return f"{today_str} — пар нет 🎉"

    lines = [f"📅 Расписание на {today_str}:"]

    for lesson in lessons:
        line = f"• {lesson.start_time}–{lesson.end_time} — {lesson.subject.name}"

        if lesson.lesson_type:
            line += f" ({lesson.lesson_type})"

        if lesson.teacher:
            line += f", {lesson.teacher}"

        if lesson.classroom:
            line += f", ауд. {lesson.classroom}"

        lines.append(line)

    return "\n".join(lines)


def format_user_week_schedule(lessons: Sequence[Lesson], week_type: str) -> str:
    week_label = "Чётная неделя" if week_type == "even" else "Нечётная неделя"

    if not lessons:
        return f"{week_label} — пар нет на этой неделе."

    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    schedule = f"📚 {week_label}\n\n"

    for day, day_group in groupby(lessons, key=lambda l: l.day_of_week):
        schedule += f"{day_names[day]}:\n"
        for lesson in day_group:
            line = f"• {lesson.start_time}–{lesson.end_time} — {lesson.subject.name}"

            if lesson.lesson_type:
                line += f" ({lesson.lesson_type})"

            if lesson.teacher:
                line += f", {lesson.teacher}"

            if lesson.classroom:
                line += f", ауд. {lesson.classroom}"

            schedule += line + "\n"
        schedule += "\n"

    return schedule.rstrip("\n")


def format_general_week_schedule(lessons: Sequence[Lesson], week_type: str) -> str:
    week_label = "Чётная неделя" if week_type == "even" else "Нечётная неделя"

    if not lessons:
        return f"{week_label} — расписание не заполнено."

    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    schedule = f"📚 {week_label} (общее расписание)\n\n"

    for day, day_group in groupby(lessons, key=lambda l: l.day_of_week):
        schedule += f"{day_names[day]}:\n"

        day_lessons = list(day_group)
        for start_time, time_group in groupby(day_lessons, key=lambda l: l.start_time):
            time_lessons = list(time_group)
            end_time = time_lessons[0].end_time

            parts = []
            for lesson in time_lessons:
                part = lesson.subject.name
                if lesson.subgroup is not None:
                    part += f" ({lesson.subgroup} подгруппа)"

                if lesson.lesson_type:
                    part += f" ({lesson.lesson_type})"

                if lesson.teacher:
                    part += f", {lesson.teacher}"

                if lesson.classroom:
                    part += f", ауд. {lesson.classroom}"

                parts.append(part)

            line = f"• {start_time}–{end_time} — {' | '.join(parts)}"
            schedule += line + "\n"

        schedule += "\n"

    return schedule.rstrip("\n")