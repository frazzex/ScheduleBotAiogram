from tortoise.models import Model
from tortoise import fields


class Lesson(Model):
    id = fields.IntField(pk=True)
    subject = fields.ForeignKeyField('models.Subject', related_name='lessons')
    day_of_week = fields.IntField()
    start_time = fields.CharField(max_length=10)
    end_time = fields.CharField(max_length=10)
    lesson_type = fields.CharField(max_length=50)
    teacher = fields.CharField(max_length=255, null=True)
    classroom = fields.CharField(max_length=50, null=True)
    week_type = fields.CharField(max_length=10, null=True)
    subgroup = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "lessons"

    def __str__(self):
        return f"{self.subject.name} - {self.get_day_name()} {self.start_time}"

    def get_day_name(self) -> str:
        """Возвращает название дня недели"""
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[self.day_of_week] if 0 <= self.day_of_week < 7 else "Неизвестно"
