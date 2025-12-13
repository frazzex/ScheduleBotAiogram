from tortoise.models import Model
from tortoise import fields


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
