from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    subgroup = fields.IntField(null=True)
    group = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def __str__(self):
        return f"Пользователь {self.id} ({self.full_name})"
