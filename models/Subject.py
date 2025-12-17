from tortoise.models import Model
from tortoise import fields


class Subject(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    short_name = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "subjects"

    def __str__(self):
        return self.name
