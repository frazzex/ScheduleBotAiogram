from aiogram.fsm.state import StatesGroup, State


class SettingsState(StatesGroup):
    choose_subgroup = State()
