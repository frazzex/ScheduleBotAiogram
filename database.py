from tortoise import Tortoise
import logging

logger = logging.getLogger(__name__)

# Конфигурация для Tortoise ORM (используется aerich для миграций)
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db.sqlite3"  # Можно изменить на PostgreSQL: "postgres://user:password@localhost/dbname"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Инициализация подключения к базе данных"""
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',  # Можно изменить на PostgreSQL
        modules={'models': ['models']}
    )
    # Создаем таблицы
    await Tortoise.generate_schemas()
    logger.info("База данных инициализирована")


async def close_db():
    """Закрытие подключения к базе данных"""
    await Tortoise.close_connections()
    logger.info("Подключение к базе данных закрыто")

