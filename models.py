from tortoise.models import Model
from tortoise import fields
from typing import Optional


class User(Model):
    """Модель пользователя"""
    id = fields.BigIntField(pk=True)  # Telegram user ID
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    subgroup = fields.IntField(null=True)  # 1 или 2 подгруппа
    group = fields.CharField(max_length=50, null=True)  # Название группы
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return f"User {self.id} ({self.full_name})"

    @staticmethod
    def _is_even_week_from_september() -> bool:
        """
        Возвращает True, если текущая неделя (с 1 сентября) — чётная.
        Используется для отбора пар по типу недели.
        """
        from datetime import datetime

        today = datetime.now().date()
        september_start = datetime(today.year, 9, 1).date()
        if today < september_start:
            september_start = datetime(today.year - 1, 9, 1).date()
        days_since_september = (today - september_start).days
        week_number = days_since_september // 7 + 1
        return week_number % 2 == 0

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Преобразует время HH:MM в количество минут (для сортировки)."""
        try:
            hours, minutes = time_str.split(":")
            return int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return 0

    async def get_today_lessons(self, show_all: bool = False):
        """
        Вернуть пары на сегодня для пользователя.

        Args:
            show_all: если True — не фильтровать по подгруппе (общее расписание).

        Returns:
            list[Lesson]: отсортированный список пар на сегодня.
        """
        from datetime import datetime

        # Определяем день недели и тип недели
        weekday = datetime.now().weekday()  # 0 - понедельник
        week_type = "even" if self._is_even_week_from_september() else "odd"

        # Базовый запрос: пары на нужный день и неделю (или для обеих)
        lessons = await Lesson.filter(
            day_of_week=weekday,
            week_type__in=[week_type, None],
        ).prefetch_related("subject")

        # Фильтрация по подгруппе, если нужно
        if not show_all:
            filtered = []
            for lesson in lessons:
                # Пара без подгруппы — показываем всем
                if lesson.subgroup is None:
                    filtered.append(lesson)
                # Если у пользователя есть подгруппа — сравниваем
                elif self.subgroup is not None and lesson.subgroup == self.subgroup:
                    filtered.append(lesson)
            lessons = filtered

        # Сортируем по времени начала
        lessons.sort(key=lambda l: self._time_to_minutes(l.start_time))
        return lessons


class Subject(Model):
    """Модель предмета"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)  # Название предмета
    short_name = fields.CharField(max_length=100, null=True)  # Короткое название
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "subjects"

    def __str__(self):
        return self.name


class Lesson(Model):
    """Модель пары (урока)"""
    id = fields.IntField(pk=True)
    subject = fields.ForeignKeyField('models.Subject', related_name='lessons')
    day_of_week = fields.IntField()  # 0-Понедельник, 1-Вторник, ..., 6-Воскресенье
    start_time = fields.CharField(max_length=10)  # Формат "HH:MM"
    end_time = fields.CharField(max_length=10)  # Формат "HH:MM"
    lesson_type = fields.CharField(max_length=50)  # л, пр, лаб
    teacher = fields.CharField(max_length=255, null=True)  # Преподаватель
    classroom = fields.CharField(max_length=50, null=True)  # Аудитория
    week_type = fields.CharField(max_length=10, null=True)  # "even", "odd", или null для обеих
    subgroup = fields.IntField(null=True)  # 1, 2 или null для обеих подгрупп
    group = fields.CharField(max_length=50, null=True)  # Группа
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "lessons"

    def __str__(self):
        return f"{self.subject.name} - {self.get_day_name()} {self.start_time}"

    def get_day_name(self) -> str:
        """Возвращает название дня недели"""
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[self.day_of_week] if 0 <= self.day_of_week < 7 else "Неизвестно"

