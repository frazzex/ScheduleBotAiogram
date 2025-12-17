from functools import wraps

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.reply import get_subgroup_keyboard
from models import User
from states import SettingsState


def require_subgroup(func):
    @wraps(func)
    async def wrapper(message: Message, user: User, state: FSMContext, *args, **kwargs):
        if user.subgroup is None:
            await state.set_state(SettingsState.choose_subgroup)
            await message.answer('Сначала выберите подгруппу', reply_markup=get_subgroup_keyboard())
            return
        return await func(message, user, state, *args, **kwargs)

    return wrapper
