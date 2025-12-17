from aiogram import Router

router = Router()

from .schedule import router as schedule_router
router.include_router(schedule_router)