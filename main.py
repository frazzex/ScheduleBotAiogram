import asyncio
import logging
import sys
from os import getenv
import dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

# Bot token can be obtained via https://t.me/BotFather
dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    if is_even_week:
        schedule_even = """
           **ЧЁТНАЯ НЕДЕЛЯ**

           **Понедельник:**
           - 8:00–9:35 — «Основы российской государственности» (пр), ст. пр. Нестеров Д.В., ауд. 2219;
           - 9:45–11:20 — «Математический анализ» (л) доц. Жалнина А.А., ауд. 2115;
           - 11:45–13:20 — «Иностранный язык» (пр), доц. Сергейчик Т.С., ауд. 5203;
           - 11:45–13:20 — «Архитектура вычислительных систем» (лаб), вес. Лось М.А., ауд. 2131а;
           - 13:30–15:05 — «Циклические виды спорта (по выбору)» (пр), ст. пр. Тюкалова С.А., лыжная база.

           **Вторник:**
           - 9:45–11:20 — «Языки программирования» (лаб), асс. Дунанов И.О., ауд. 21306;
           - 11:45–13:20 — «История России» (пр), асс. Сирюкин И.В., ауд. 5221;
           - 13:30–15:05 — «Основы российской государственности» (л) доц. Пьянов А.Е., ауд. 4бл;
           - 15:30–17:05 — «Информатика» (л), зав. каф. Степанов Ю.А., ауд. 2226;

           **Среда:**
           - 9:45–11:20 — «Математический анализ» (пр), асс. Ануфриев Д.А., ауд. 5121;
           - 11:45–13:20 — «Циклические виды спорта (по выбору)» (пр), ст. пр. Тюкалова С.А., лыжная база;
           - 13:30–15:05 — «История России» (л), ст. пр. Ганенок В.Ю., ауд. 2бл;
           - 15:30–17:05 — «Алгебра и геометрия» (пр), проф. Медведев А.В., ауд. 5106.
           """
        await message.answer(schedule_even)
    else:
        schedule_odd = """
           **НЕЧЁТНАЯ НЕДЕЛЯ**

           **Понедельник:**
           - 8:00–9:35 — «Основы российской государственности» (пр), ст. пр. Нестеров Д.В., ауд. 2219;
           - 9:45–11:20 — «Математический анализ» (л) доц. Жалнина А.А., ауд. 2115;
           - 11:45–13:20 — «Архитектура вычислительных систем» (лаб), асс. Лось М.А., ауд. 2131в;
           - 11:45–13:20 — «Иностранный язык» (пр), доц. Сергейчик Т.С., ауд. 5203;
           - 13:30–15:05 — «Циклические виды спорта (по выбору)» (пр), ст. пр. Тюкалова С.А., лыжная база.

           **Вторник:**
           - 9:45–11:20 — «Языки программирования» (лаб), асс. Дунанов И.О., ауд. 21306;
           - 11:45–13:20 — «История России» (пр), асс. Сирюкин И.В., ауд. 5221;
           - 13:30–15:05 — «Введение в профессиональную деятельность» (л), доц. Бондарева Л.В., ауд. 2219;
           - 15:30–17:05 — «Информатика» (л), зав. каф. Степанов Ю.А., ауд. 2226;

           **Среда:**
           - 9:45–11:20 — «Математический анализ» (пр), асс. Ануфриев Д.А., ауд. 5121;
           - 11:45–13:20 — «Циклические виды спорта (по выбору)» (пр), ст. пр. Тюкалова С.А., лыжная база;
           - 13:30–15:05 — «История России» (л), ст. пр.  Ганенок В.Ю., ауд. 2бл;
           - 15:30–17:05 — «Алгебра и геометрия» (пр), проф. Медведев А.В., ауд. 5106.
           """
        await message.answer(schedule_odd)


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())