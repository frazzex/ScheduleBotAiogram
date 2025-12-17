from datetime import date
from typing import Sequence

from tortoise.expressions import Q

from models import Lesson
from models import User
from utils.common import time_to_minutes, is_even_week_from_september


async def get_general_week_lessons(week_t: str) -> Sequence[Lesson]:
    query = (Lesson
             .filter(week_type=week_t)
             .prefetch_related("subject"))

    lessons = await query

    lessons = sorted(
        lessons,
        key=lambda l: (
            l.day_of_week,
            time_to_minutes(l.start_time),
            l.subgroup or 0
        )
    )

    return lessons


async def get_user_week_lessons(user: User, week_type: str) -> Sequence[Lesson]:
    query = (Lesson.filter(week_type=week_type)
             .filter(Q(subgroup=user.subgroup) | Q(subgroup__isnull=True))
             .prefetch_related("subject"))

    lessons = await query

    lessons = sorted(
        lessons,
        key=lambda l: (
            l.day_of_week,
            time_to_minutes(l.start_time),
            l.subgroup or 0
        )
    )

    return lessons


async def get_today_lessons_for_user(user: User) -> Sequence[Lesson]:
    today = date.today()
    weekday = today.weekday()

    week_type = "even" if is_even_week_from_september(today) else "odd"

    query = (Lesson.filter(day_of_week=weekday, week_type=week_type)
             .filter(Q(subgroup=user.subgroup) | Q(subgroup__isnull=True))
             .prefetch_related("subject"))

    lessons = await query

    lessons = sorted(lessons, key=lambda l: time_to_minutes(l.start_time))

    return lessons
