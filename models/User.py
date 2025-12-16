from datetime import datetime

from tortoise.models import Model
from tortoise import fields

from .Lesson import Lesson


class User(Model):
    """Модель пользователя"""
    id = fields.BigIntField(pk=True)  # Telegram user ID
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    subgroup = fields.IntField(null=True)  # 1 или 2 подгруппа
    group = fields.CharField(max_length=50, null=True)  # Название группы
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def __str__(self):
        return f"User {self.id} ({self.full_name})"

    # ===== Вспомогательные методы =====
    @staticmethod
    def _is_even_week_from_september() -> bool:
        """
        Возвращает True, если текущая неделя (с 1 сентября) — чётная.
        Нужен для выбора расписания по типу недели.
        """
        today = datetime.now().date()
        september_start = datetime(today.year, 9, 1).date()
        if today < september_start:
            september_start = datetime(today.year - 1, 9, 1).date()
        days_since_september = (today - september_start).days
        week_number = days_since_september // 7 + 1
        return week_number % 2 == 0

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Преобразует строку времени HH:MM в минуты (для сортировки)."""
        try:
            hours, minutes = time_str.split(":")
            return int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return 0

    # ===== Публичный метод =====
    async def get_today_lessons(self, show_all: bool = False) -> list[Lesson]:
        """
        Вернёт список пар на сегодня для пользователя.

        :param show_all: если True — не фильтровать по подгруппе (общее расписание)
        :return: список объектов Lesson, отсортированных по времени
        """
        # День недели: 0 - понедельник, 6 - воскресенье
        weekday = datetime.now().weekday()
        week_type = "even" if self._is_even_week_from_september() else "odd"

        # Базовый запрос: пары на нужный день и неделю (или для обеих)
        lessons = await Lesson.filter(
            day_of_week=weekday,
            week_type__in=[week_type, None],
        ).prefetch_related("subject")

        # Фильтрация по подгруппе, если нужно
        if not show_all:
            filtered: list[Lesson] = []
            for lesson in lessons:
                # Пара без подгруппы подходит всем
                if lesson.subgroup is None:
                    filtered.append(lesson)
                # Если указана подгруппа у пары и у пользователя — сравниваем
                elif self.subgroup is not None and lesson.subgroup == self.subgroup:
                    filtered.append(lesson)
            lessons = filtered

        # Сортируем по времени начала
        lessons.sort(key=lambda l: self._time_to_minutes(l.start_time))
        return lessons
