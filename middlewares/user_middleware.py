from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from models import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            user = await User.get_or_create(
                id=user_id,
                defaults={
                    "username": event.from_user.username,
                    "full_name": event.from_user.full_name
                }
            )
            data["user"] = user[0]

        return await handler(event, data)
