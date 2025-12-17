import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from handlers import router
from middlewares.user_middleware import UserMiddleware
from database import init_db, close_db

load_dotenv()

ENVIRONMENT = os.getenv('ENVIRONMENT')

if not ENVIRONMENT:
    raise ValueError('ENVIRONMENT не найден в .env файле!')

match ENVIRONMENT:
    case 'dev':
        BOT_TOKEN = os.getenv('BOT_TOKEN_DEV')
    case 'prod':
        BOT_TOKEN = os.getenv('BOT_TOKEN_PROD')
    case _:
        raise ValueError('Некорректный ENVIRONMENT в .env файле!')


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=None)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.include_router(router)

    await init_db()

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
